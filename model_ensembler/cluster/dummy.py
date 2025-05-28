import asyncio
import logging
import random
import subprocess
import threading

from model_ensembler.cluster import Job, job_lock
from model_ensembler.utils import Arguments


START_STATES = ("SUBMITTED", "RUNNING")
FINISH_STATES = ("COMPLETED", "FAILED")

_dict_lock = threading.Lock()
_jobs = dict()


def threaded_job(run_dir, script):
    """Dummy method to set off local job

    Args:
        run_dir (str): Directory script is running in.
        script (str): Name of script to run.
    """
    global _jobs

    with _dict_lock:
        _jobs[run_dir] = Job(_jobs[run_dir].name,
                             "RUNNING",
                             True,
                             False)

    logging.info("DUMMY RUN: {} - {}".format(run_dir, _jobs[run_dir]))
    subprocess.run("./{}".format(script), cwd=run_dir)

    # TODO: failed
    with _dict_lock:
        _jobs[run_dir] = Job(_jobs[run_dir].name,
                             "COMPLETED",
                             True,
                             True)


async def find_id(job_id):
    """Dummy method to find local job id.

    Args:
        job_id (int): Local job identifier.

    Returns:
        (int): job id.

    Raises:
        LookupError: If job id not found.
    """
    global _jobs

    job = None
    job_arr = [el for el in _jobs.values() if el.name == job_id]

    if len(job_arr) == 1:
        job = job_arr[0]
    elif len(job_arr) > 1:
        raise LookupError("{} jobs found for ID {}".format(len(job_arr),
                                                           job_id))
    return job


async def current_jobs(ctx, match):
    """Dummy method to find current jobs.

    Args:
        ctx (object): Context object for retrieving configuration.
        match (str): Jobs to match the job list with.

    Returns:
        (list): Current jobs.
    """
    global _jobs

    job_arr = [el for el in _jobs.values()
               if el.name.startswith(match)
               and el.state in START_STATES]

    return job_arr


async def submit_job(ctx, script=None):
    """Dummy method to submit job locally.

    Args:
        ctx (object): Context object for retrieving configuration.
        script (str): Script name to submit.

    Returns:
        (int): Job ID.
    """
    # TODO: ugh, we could use contextvars for this
    global _jobs
    args = Arguments()

    max_submit_sleep = args.max_stagger
    sleep_for = random.randint(0, max_submit_sleep)
    logging.debug(
        "Sleeping for {} seconds before submission".format(sleep_for))
    await asyncio.sleep(sleep_for)

    with _dict_lock:
        _jobs[ctx.dir] = Job(ctx.id, "SUBMITTED", False, False)

    threading.Thread(target=threaded_job, args=(ctx.dir, script)).start()
    return ctx.id

if __name__ == "__main__":
    pass
