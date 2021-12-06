import asyncio
import collections
import contextvars
import importlib
import logging
import os
import shlex
import shutil

from datetime import datetime
from pprint import pformat

import jinja2

import model_ensembler

from model_ensembler.tasks import \
    CheckException, TaskException, ProcessingException
from model_ensembler.tasks.hpc import init_hpc_backend
from model_ensembler.utils import Arguments

batch_ctx = contextvars.ContextVar("batch_ctx")
ctx = contextvars.ContextVar("ctx")
cluster_ctx = contextvars.ContextVar("cluster")
extra_ctx = contextvars.ContextVar("extra")


"""Main ensembler module with execution core code

"""


async def run_check(func, check):
    """Run a check configuration

    Args:
        ctx (object): context object for retrieving configuration
        func (callable): async check method
        check (dict): check configuration

    Raises:
        CheckException: any exception from the called check
    """
    result = False
    args = Arguments()

    while not result:
        try:
            logging.debug("PRE CHECK")
            run_ctx = ctx.get()
            result = await func(run_ctx, **check.args)
            logging.debug("POST CHECK")
        except Exception as e:
            logging.exception(e)
            raise CheckException("Issues with flight checks, abandoning")

        if not result:
            logging.debug("Cannot continue, waiting {} seconds for next check".
                          format(args.check_timeout))
            await asyncio.sleep(args.check_timeout)


async def run_task(func, task):
    """Run a task configuration

    Args:
        ctx (object): context object for retrieving configuration
        func (callable): async task method
        task (dict): task configuration

    Raises:
        TaskException: any exception from the called task
    """
    try:
        args = dict() if not task.args else task.args
        run_ctx = ctx.get()
        await func(run_ctx, **args)
    except Exception as e:
        logging.exception(e)
        raise TaskException("Issues with flight checks, abandoning")
    return True


async def run_task_items(items):
    """Run a set of task and checks

    Run the list of tasks and check items, the configuration references the
    ``model_ensemble.tasks`` method to use and the context/configuration
    provides the arguments. TaskException and CheckException are trapped and
    rethrown as ProcessingException

    Args:
        ctx (object): context object for retrieving configuration
        tasks (list): a list of tasks and checks

    Raises:
        ProcessingException: a common exception thrown for failures in the
        individual tasks
    """
    try:
        for item in items:
            func = getattr(model_ensembler.tasks, item.name)

            logging.debug("TASK CWD: {}".format(os.getcwd()))
            logging.debug("TASK CTX: {}".format(pformat(ctx.get())))
            logging.debug("TASK FUNC: {}".format(pformat(item)))

            # TODO: insert ctx into decorators (reflected methods)
            if func.check:
                await run_check(func, item)
            else:
                await run_task(func, item)
    except (TaskException, CheckException) as e:
        raise ProcessingException(e)


# CORE EXECUTION FOR BATCHER
#
async def run_runner(limit, tasks):
    """Runs a list of tasks asynchronously

    Given a particular limit, establish a semaphore and run up to limit tasks.
    Once the list of tasks is complete, return

    Args:
        limit (int): context object for retrieving configuration
        tasks (list): a list of tasks and checks
    """

    # TODO: return run task windows/info
    sem = asyncio.Semaphore(limit)

    async def sem_task(task):
        async with sem:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


def process_templates(template_list):
    """Render templates based on provided context

    Args:
        ctx (object): context object for retrieving configuration
        template_list (list): list of paths to template sources
    """
    run_ctx = ctx.get()

    for tmpl_file in template_list:
        if tmpl_file[-3:] != ".j2":
            raise RuntimeError("{} doe not appear to be a Jinja2 template "
                               "(.j2)".format(tmpl_file))

        tmpl_path = os.path.join(run_ctx.dir, tmpl_file)
        with open(tmpl_path, "r") as fh:
            tmpl_data = fh.read()

        dst_file = tmpl_path[:-3]
        logging.info("Templating {} to {}".format(tmpl_path, dst_file))
        tmpl = jinja2.Template(tmpl_data)
        dst_data = tmpl.render(run=run_ctx)
        with open(dst_file, "w+") as fh:
            fh.write(dst_data)
        os.chmod(dst_file, os.stat(tmpl_path).st_mode)

        os.unlink(tmpl_path)


_batch_job_sems = dict()


async def run_batch_item(run):
    """Execute a run configuration

    Args:
        run (object): specific run configuration
        batch (object): whole batch configuration
    """

    # TODO: my understanding is that all context from here through to end
    #  methods/tasks will now be under run_context in do_batch_execution
    batch = batch_ctx.get()
    ctx.set(run)
    cluster = cluster_ctx.get()

    logging.info("Start run {} at {}".format(run.id, datetime.utcnow()))
    logging.debug(pformat(run))

    args = Arguments()

    if args.pickup and os.path.exists(run.dir):
        if not os.path.exists(run.dir):
            raise RuntimeError("Pickup previous run dir {} cannot work, it "
                               "doesn't exist".format(run.dir))

        logging.info("Picked up previous job directory for run {}".
                     format(run.id))

        for tmpl_file in batch.templates:
            src_path = os.path.join(batch.templatedir, tmpl_file)
            dst_path = shutil.copy(src_path, os.path.join(run.dir, tmpl_file))
            logging.info("Re-copied {} to {} for template regeneration".
                         format(src_path, dst_path))
    else:
        if os.path.exists(run.dir):
            raise RuntimeError("Run directory {} already exists".
                               format(run.dir))

        os.makedirs(run.dir, mode=0o775)

        cmd = "rsync -aXE {}/ {}/".format(batch.templatedir, run.dir)
        logging.info(cmd)
        proc = await asyncio.create_subprocess_exec(*shlex.split(cmd))
        rc = await proc.wait()

        if rc != 0:
            raise RuntimeError("Could not grab template directory {} to {}".
                               format(batch.templatedir, run.dir))

    process_templates(batch.templates)

    try:
        await run_task_items(batch.pre_run)

        if args.no_submission:
            logging.info("Skipping actual slurm submission based on arguments")
        else:
            async with _batch_job_sems[batch.name]:
                func = getattr(model_ensembler.tasks, "jobs")
                check = collections.namedtuple("check", ["args"])

                await run_check(func, check({
                    "limit": batch.maxjobs,
                    "match": batch.name,
                }))

                job_id = await cluster.submit_job(run, script=batch.job_file)

                if not job_id:
                    logging.exception(
                        "{} could not be submitted, we won't continue".format(
                            batch.name
                        ))
                else:
                    running = False
                    state = None

                    while not running:
                        try:
                            job = await cluster.find_id(job_id)
                            state = job.state
                        except (IndexError, ValueError) as e:
                            logging.warning("Job {} not registered yet, "
                                            "or error encountered".
                                            format(job_id))
                            logging.exception(e)

                        if state and (state in cluster.START_STATES):
                            running = True
                        else:
                            await asyncio.sleep(args.submit_timeout)

                    while True:
                        try:
                            job = await cluster.find_id(job_id)
                            state = job.state
                        except (IndexError, ValueError):
                            logging.exception("Job status for run {} retrieval"
                                              " whilst slurm running, waiting "
                                              "and retrying".
                                              format(run.id))
                            await asyncio.sleep(args.error_timeout)
                            continue

                        logging.debug("{} monitor got state {} for job {}".
                                      format(run.id, state, job_id))

                        if state in cluster.FINISH_STATES:
                            logging.info("{} monitor got state {} for job {}".
                                         format(run.id, state, job_id))
                            break
                        else:
                            await asyncio.sleep(args.running_timeout)

        await run_task_items(batch.post_run)
    except ProcessingException:
        logging.exception("Run failure caught, abandoning {} but not the "
                          "batch".format(run.id))
        return

    logging.info("End run {} at {}".format(run.id, datetime.utcnow()))


def do_batch_execution(loop, batch):
    """Execute a batch configuration

    Args:
        loop (object): event loop
        batch (object): batch configuration
    """

    logging.info("Start batch: {}".format(datetime.utcnow()))
    logging.debug(pformat(batch))

    args = Arguments()
    batch_ctx.set(batch)
    batch_tasks = list()
    _batch_job_sems[batch.name] = asyncio.Semaphore(batch.maxjobs)

    batch_dict = {k: v for k, v in batch._asdict().items() \
                  if not (k.startswith("pre_") or k.startswith("post_")
                          or k == "runs")}

    run_vars = ctx.get()
    run_vars.update(batch_dict)
    ctx.set(run_vars)

    # We are process dependent here, so this is where we have the choice of
    # concurrency strategies but each batch
    # is dependent on chdir remaining consistent after this point.
    orig = os.getcwd()
    if not os.path.exists(batch.basedir):
        os.makedirs(batch.basedir, exist_ok=True)
    os.chdir(batch.basedir)

    loop.run_until_complete(run_task_items(batch.pre_batch))

    for idx, run in enumerate(batch.runs):
        # Auto-generated context vars for run
        run['id'] = "{}-{}".format(batch.name, batch.runs.index(run))
        run['dir'] = os.path.abspath(os.path.join(os.getcwd(), run['id']))

        if idx < args.skips:
            logging.warning("Skipping run index {} due to {} skips, run ID: "
                            "{}".format(idx, args.skips, run['id']))
            continue

        if args.indexes and idx not in args.indexes:
            logging.warning("Skipping run index {} due to not being in "
                            "indexes argument, run ID: {}".
                            format(idx, run['id']))
            continue

        # At this point the context changes at root to property based
        ctx_dict = ctx.get()
        ctx_dict.update(run)
        ctx_dict.update(extra_ctx.get())

        Run = collections.namedtuple('Run', field_names=ctx_dict.keys())
        r = Run(**ctx_dict)
        task = run_batch_item(r)
        batch_tasks.append(task)

    loop.run_until_complete(run_runner(batch.maxruns, batch_tasks))

    loop.run_until_complete(run_task_items(batch.post_batch))

    os.chdir(orig)
    logging.info("Batch {} completed: {}".
                 format(batch.name, datetime.utcnow()))
    # TODO: return batch windows/info
    return "Success"


class BatchExecutor(object):
    """Create an executor for a ensemble configuration

    The purpose of this is act as the extensible master executor for the
    ensemble configuration provided. It handles the event loop and should be
    used to contain and control the execution overall
    """

    def __init__(self, cfg, backend="slurm", extra_vars=[]):
        """Constructor

        Args:
            cfg (object): EnsembleConfig ensemble configuration
        """
        self._cfg = cfg

        self._init_cluster(backend)
        self._init_ctx(extra_vars)

    def _init_cluster(self, backend):
        """Initialise the cluster backend for batch execution

        Args:
            backend (string): identifier for backend in
            `model_ensembler.cluster`
        """
        nom = "model_ensembler.cluster.{}".format(backend)
        try:
            mod = importlib.import_module(nom)
        except ModuleNotFoundError:
            raise NotImplementedError("No {} implementation exists in "
                                      "model_ensembler.cluster!".
                                      format(backend))

        init_hpc_backend(nom)
        cluster_ctx.set(mod)

    def _init_ctx(self, extra_vars):
        """Initialise contexts

        Initialise the root context vars for batch execution and set
        extra context vars that can be added last thing to the run
        """
        var_dict = ctx.get(dict())
        var_dict.update(self._cfg.vars)
        ctx.set(var_dict)

        extra_ctx.set(extra_vars)

    def run(self):
        """Run the executor

        This will establish the event loop, run the preprocessing actions for
        the ensemble, cycle through executing the batches and then run
        postprocessing actions. Exceptions will be caught and the event loop
        closed, currently with no specific handling

        Args:
            loop (object): event loop
            batch (object): whole batch configuration
        """
        logging.info("Running batcher")

        loop = None

        try:
            loop = asyncio.get_event_loop()

            # TODO: test - loop outside context or vice versa?
            loop.run_until_complete(
                run_task_items(self._cfg.pre_process))

            for batch in self._cfg.batches:
                do_batch_execution(loop, batch)

            loop.run_until_complete(
                run_task_items(self._cfg.post_process))

        # TODO: provide except block for user specified handling of failures

        finally:
            if loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
