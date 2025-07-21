import asyncio
import collections
import contextvars
import importlib
import logging
import os

from datetime import datetime
from pprint import pformat

import model_ensembler

from model_ensembler.exceptions import TemplatingError
from model_ensembler.tasks.exceptions import ProcessingException
from model_ensembler.tasks.hpc import init_hpc_backend
from model_ensembler.utils import Arguments

from model_ensembler.templates import \
    prepare_run_directory, process_templates
from model_ensembler.runners import run_check, run_runner, run_task_items

batch_ctx = contextvars.ContextVar("batch")
run_ctx = contextvars.ContextVar("run")
cluster_ctx = contextvars.ContextVar("cluster")
extra_ctx = contextvars.ContextVar("extra")


"""Main ensembler module with execution core code

"""

_batch_job_sems = dict()


async def run_batch_item(run):
    """Execute a run configuration.

    Args:
        run (object): Specific run configuration.

    Returns:
        job_id (int): Job id number.
        run (object): Specific run configuration.

    Raises:
        TemplatingError: If a job cannot be templated.
        ProcessingException: If an individual run failure is caught.
    """

    # TODO: my understanding is that all context from here through to end
    #  methods/tasks will now be under run_context in do_batch_execution
    batch = batch_ctx.get()
    run_ctx.set(run)
    cluster = cluster_ctx.get()

    logging.info("Start run {} at {}".format(run.id, datetime.utcnow()))
    logging.debug(pformat(run))

    args = Arguments()
    job_id = None

    try:
        await prepare_run_directory(batch, run)
        process_templates(run, batch.templates)
    except TemplatingError as e:
        # We catch gracefully and just prevent the run from happening
        logging.error("We cannot template the job {}: {}".format(run.id, e))
        return job_id, run

    # It's very tempting to move pre_run, but don't: we DO NOT execute until
    # job is templated. Instead I've created the ability to run tasks prior
    # to preparation/templating of the job for scenarios where you don't want
    # the templating to error out/job to even be prepared
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

                        if state and (
                                state in cluster.START_STATES or
                                state in cluster.FINISH_STATES):
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
        logging.error("Run failure caught, abandoning {} but not the "
                      "batch".format(run.id))

    logging.info("End run {} at {}".format(run.id, datetime.utcnow()))
    return job_id, run


def do_batch_execution(loop, batch, repeat=False):
    """Execute a batch configuration.

    Args:
        loop (object): Event loop.
        batch (object): Batch configuration.
        repeat (number): Loop n times.

    Returns:
        (str): Prints "Success" on completion.

    Raises:
        ProcessingException: If there is pre or post_batch processing error.
    """

    logging.info("Start batch: {}".format(datetime.utcnow()))
    logging.debug(pformat(batch))

    args = Arguments()
    skip_indexes = args.indexes if args.indexes else list()
    batch_ctx.set(batch)

    batch_dict = {k: v
                  for k, v in batch._asdict().items() \
                  if not (k.startswith("pre_")
                          or k.startswith("post_")
                          or k in "runs")
                  and not (k in ["cluster", "email", "nodes", "ntasks", "length"]
                           and v is None)}

    run_vars = run_ctx.get()
    run_vars.update(batch_dict)
    run_ctx.set(run_vars)

    # We are process dependent here, so this is where we have the choice of
    # concurrency strategies but each batch
    # is dependent on chdir remaining consistent after this point.
    orig = os.getcwd()
    if not os.path.exists(batch.basedir):
        os.makedirs(batch.basedir, exist_ok=True)
    os.chdir(batch.basedir)

    # TODO: Gross implementation for #26 - repeat parameter, this should be
    #  abstracted away into executor implementations (BatchExecutor.execute)
    #  and made to work better
    if not repeat:
        repeat_count = 2
    else:
        logging.warning("We are due to repeat until a batch check fails us")
        repeat_count = 1000000

    for rep_i in range(1, repeat_count):
        logging.info("Running cycle {}".format(rep_i))

        batch_tasks = list()
        _batch_job_sems[batch.name] = asyncio.Semaphore(batch.maxjobs)

        try:
            loop.run_until_complete(run_task_items(batch.pre_batch))
        except ProcessingException:
            logging.error("We have received a pre_batch failure, "
                          "will stop execution")
            break

        if len(sorted(set(skip_indexes))) == len(batch.runs):
            logging.error("No longer able to run this batch, all runs are in "
                          "the indexes to skip")
            break

        for idx, run in enumerate(batch.runs):
            # Auto-generated context vars for run
            run['idx'] = idx
            run['id'] = "{}-{}".format(batch.name, run['idx'])
            run['dir'] = os.path.abspath(os.path.join(os.getcwd(), run['id']))
            run['batch_idx'] = rep_i

            if idx < args.skips:
                logging.warning("Skipping run index {} due to {} skips, run "
                                "ID: {}".format(idx, args.skips, run['id']))
                continue

            if idx in skip_indexes:
                logging.warning("Skipping run index {} due to being in "
                                "skip indexes, run ID: {}".
                                format(idx, run['id']))
                continue

            # At this point the context changes at root to property based
            ctx_dict = run_ctx.get()
            ctx_dict.update(run)
            ctx_dict.update(extra_ctx.get())

            Run = collections.namedtuple('Run', field_names=ctx_dict.keys())
            r = Run(**ctx_dict)
            task = run_batch_item(r)
            batch_tasks.append(task)

        batch_results = loop.run_until_complete(
            run_runner(batch.maxruns, batch_tasks))

        for idx, result in enumerate(batch_results):
            job, run = result
            logging.debug("Batch {} result #{} from run {}: job {}".format(
                batch.name, idx, run.idx, str(job)
            ))

            if not job and run.idx not in skip_indexes:
                logging.warning("Result #{} for run {} indicates unsuccessful "
                                "submission, adding to indexes to skip".
                                format(idx, run.idx))
                skip_indexes.append(run.idx)

        try:
            loop.run_until_complete(run_task_items(batch.post_batch))
        except ProcessingException:
            logging.error("We have received a post_batch failure, "
                          "will stop execution")
            break

    os.chdir(orig)
    logging.info("Batch {} completed: {}".
                 format(batch.name, datetime.utcnow()))
    # TODO: return batch windows/info
    return "Success"


class BatchExecutor(object):
    """Create an executor for a ensemble configuration.

    The purpose of this is act as the extensible master executor for the
    ensemble configuration provided. It handles the event loop and should be
    used to contain and control the execution overall.
    """

    def __init__(self, cfg, backend="slurm", extra_vars=[]):
        """Constructor.

        Args:
            cfg (object): EnsembleConfig ensemble configuration.
            backend (str): Backend to execute on,
                        should be one of {'dummy'|'slurm'}.
            extra_vars (list): Additional variables.
        """
        self._cfg = cfg

        self._init_cluster(backend)
        self._init_ctx(extra_vars)

    def _init_cluster(self, backend):
        """Initialise the cluster backend for batch execution.

        Args:
            backend (str): identifier for backend in
            `model_ensembler.cluster`.

        Raises:
            ModuleNotFoundError: If cluster backend specified is not supported.
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
        """Initialise contexts.

        Initialise the root context vars for batch execution and set
        extra context vars that can be added last thing to the run.

        Args:
            extra_vars (list): Additional variables.
        """
        var_dict = run_ctx.get(dict())
        var_dict.update(self._cfg.vars)
        run_ctx.set(var_dict)

        extra_ctx.set(extra_vars)

    def run(self, loop=None):
        """Run the executor.

        This will establish the event loop, run the preprocessing actions for
        the ensemble, cycle through executing the batches and then run
        postprocessing actions. Exceptions will be caught and the event loop
        closed, currently with no specific handling.

        Args:
            loop (object): Event loop.
        """
        logging.info("Running batcher")

        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                run_task_items(self._cfg.pre_process))

            # Should batch be in function signature?
            for batch in self._cfg.batches:
                do_batch_execution(loop, batch, repeat=batch.repeat)
                # do_batch_execution(loop, batch) moves to
                # self.execute(loop, batch)

            loop.run_until_complete(
                run_task_items(self._cfg.post_process))

        finally:
            if loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

# What does this do?
    def execute(self, loop, batch):
        raise NotImplementedError("")
