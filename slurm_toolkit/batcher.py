import asyncio
import collections
import concurrent.futures
import logging
import os
import random
import shlex
import subprocess
import time

from datetime import datetime
from pprint import pformat

import jinja2
from pyslurm import config, job

import slurm_toolkit

from .tasks import CheckException, TaskException, ProcessingException
from .tasks import submit as slurm_submit
from .tasks.utils import execute_command
from .utils import Arguments


async def run_check(ctx, func, check):
    result = False
    args = Arguments()

    while not result:
        try:
            result = await func(ctx, **check.args)
        except Exception as e:
            logging.exception(e)
            raise CheckException("Issues with flight checks, abandoning")

        if not result:
            logging.info("Cannot continue, waiting {} seconds for next check".format(args.check_timeout))
            await asyncio.sleep(args.check_timeout)


async def run_task(ctx, func, task):
    try:
        args = dict() if not task.args else task.args
        await func(ctx, **args)
    except Exception as e:
        logging.exception(e)
        raise TaskException("Issues with flight checks, abandoning")
    return True


async def run_task_items(ctx, items):
    try:
        for item in items:
            func = getattr(slurm_toolkit.tasks, item.name)

            logging.debug("TASK CWD: {}".format(os.getcwd()))
            logging.debug("TASK CTX: {}".format(pformat(ctx)))
            logging.debug("TASK FUNC: {}".format(pformat(item)))

            if func.check:
                await run_check(ctx, func, item)
            else:
                await run_task(ctx, func, item)
    except (TaskException, CheckException) as e:
        raise ProcessingException(e)


## CORE EXECUTION FOR BATCHER
#
async def run_runner(limit, tasks):
    sem = asyncio.Semaphore(limit)

    async def sem_task(task):
        async with sem:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


async def run_batch_item(run, batch):
    logging.info("Start run {}".format(run))

    if os.path.exists(run.dir):
        raise RuntimeError("Run directory {} already exists".format(run.dir))

    os.makedirs(run.dir, mode=0o775)

    cmd = "rsync -aXE {}/ {}/".format(batch.templatedir, run.dir)
    logging.info(cmd)
    proc = await asyncio.create_subprocess_exec(*shlex.split(cmd))
    rc = await proc.wait()

    if rc != 0:
        raise RuntimeError("Could not grab template directory {} to {}".format(
            batch.templatedir, run.dir
        ))

    for tmpl_file in batch.templates:
        if tmpl_file[-3:] != ".j2":
            raise RuntimeError("{} doe not appear to be a Jinja2 template (.j2)".format(tmpl_file))

        tmpl_path = os.path.join(run.dir, tmpl_file)
        with open(tmpl_path, "r") as fh:
            tmpl_data = fh.read()

        dst_file = tmpl_path[:-3]
        logging.info("Templating {} to {}".format(tmpl_path, dst_file))
        tmpl = jinja2.Template(tmpl_data)
        dst_data = tmpl.render(run=run)
        with open(dst_file, "w+") as fh:
            fh.write(dst_data)
        os.chmod(dst_file, os.stat(tmpl_path).st_mode)

        os.unlink(tmpl_path)

    await run_task_items(run, batch.pre_run)

    if Arguments().nosubmission:
        logging.info("Skipping actual slurm submission based on arguments")
    else:
        slurm_id = await slurm_submit(run, script=batch.job_file)
        slurm_running = False
        slurm_state = None

        while not slurm_running:
            try:
                slurm_state = job().find_id(int(slurm_id))[0]['job_state']
            except ValueError:
                logging.warning("Job {} not registered yet".format(slurm_id))

            if slurm_state and (slurm_state in (
                    "COMPLETING", "PENDING", "RESV_DEL_HOLD", "RUNNING", "SUSPENDED"
                                                                         "RUNNING", "COMPLETED", "FAILED",
                    "CANCELLED")):
                slurm_running = True
            else:
                # TODO: Configurable sleeps please!
                await asyncio.sleep(2.)

        while True:
            slurm_state = job().find_id(int(slurm_id))[0]['job_state']
            logging.info("{} monitor got state {} for job {}".format(
                run.id, slurm_state, slurm_id))

            if slurm_state in ("COMPLETED", "FAILED", "CANCELLED"):
                break
            else:
                await asyncio.sleep(10.)

    await run_task_items(run, batch.post_run)
    logging.info("End run")


def do_batch_execution(loop, batch):
    logging.info(pformat(batch))
    logging.warning("Start: {}".format(datetime.utcnow()))

    batch_tasks = list()

    # We are process dependent here, so this is where we have the choice of concurrency strategies but each batch
    # is dependent on chdir remaining consistent after this point.
    orig = os.getcwd()
    if not os.path.exists(batch.basedir):
        os.makedirs(batch.basedir, exist_ok=True)
    os.chdir(batch.basedir)

    loop.run_until_complete(run_task_items(batch, batch.pre_batch))

    for run in batch.runs:
        runid = "{}-{}".format(batch.name, batch.runs.index(run))

        # TODO: Not really the best way of doing this, use some appropriate typing for all the data used
        run_vars = collections.defaultdict()
        # This dir parameters becomes very important for running commands in the correct directory context
        run['id'] = runid
        run['dir'] = os.path.abspath(os.path.join(os.getcwd(), runid))

        batch_dict = batch._asdict()
        for k, v in batch_dict.items():
            if not k.startswith("pre_") and not k.startswith("post_") and k != "runs":
                run_vars[k] = v

        run_vars.update(run)

        Run = collections.namedtuple('Run', field_names=run_vars.keys())
        r = Run(**run_vars)
        task = run_batch_item(r, batch)
        batch_tasks.append(task)

    loop.run_until_complete(run_runner(batch.maxruns, batch_tasks))

    loop.run_until_complete(run_task_items(batch, batch.post_batch))

    os.chdir(orig)
    logging.info("Batch {} completed: {}".format(batch.name, datetime.utcnow()))
    return "Success"


class BatchExecutor(object):
    def __init__(self, cfg):
        self._cfg = cfg

    def run(self):
        logging.info("Running batcher")
        loop = None

        try:
            loop = asyncio.get_event_loop()

            for batch in self._cfg.batches:
                loop.run_until_complete(run_task_items(self._cfg.vars, self._cfg.pre_process))
                do_batch_execution(loop, batch)
                loop.run_until_complete(run_task_items(self._cfg.vars, self._cfg.post_process))
        finally:
            if loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()
