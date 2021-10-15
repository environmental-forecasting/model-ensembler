import asyncio
import atexit
import collections
import concurrent.futures
import logging
import os
import subprocess

from model_ensembler.cluster import Job, job_lock


START_STATES = ("SUBMITTED", "RUNNING")
FINISH_STATES = ("COMPLETED", "FAILED")


_executor = None
_jobs = collections.OrderedDict()


def threaded_job(run_dir, script):
    global _jobs

    _jobs[run_dir].state = "RUNNING"
    _jobs[run_dir].started = True

    subprocess.run(script, cwd=run_dir)

    # TODO: failed
    _jobs[run_dir].state = "COMPLETED"
    _jobs[run_dir].finished = True


async def find_id(job_id):
    global _jobs

    job = None
    job_arr = [el for el in _jobs if el.id == job_id]

    if len(job_arr) == 1:
        job = job_arr[0]
    elif len(job_arr) > 1:
        raise LookupError("{} jobs found for ID {}".format(len(job_arr),
                                                           job_id))
    return job


async def current_jobs(ctx, match):
    global _jobs

    job_arr = [el for el in _jobs if el.id.startswith(match)]

    return job_arr


async def submit_job(ctx, script=None):
    global _executor, _jobs

    if not _executor:
        logging.info("Creating dummy thread executor with {} threads".
                     format(ctx.maxjobs))
        _executor = concurrent.futures.ThreadPoolExecutor(ctx.maxjobs)

    _jobs[ctx.dir] = Job(ctx.id, "SUBMITTED", False, False)

    _executor.submit(threaded_job, ctx.dir, script)


if __name__ == "__main__":
    pass
