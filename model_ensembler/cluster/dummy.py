import asyncio
import atexit
import collections
import concurrent.futures
import logging
import os
import subprocess
import threading

from model_ensembler.cluster import Job, job_lock


START_STATES = ("SUBMITTED", "RUNNING")
FINISH_STATES = ("COMPLETED", "FAILED")

_dict_lock = threading.Lock()
_jobs = dict()


def threaded_job(run_dir, script):
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
    global _jobs

    job_arr = [el for el in _jobs.values()
               if el.name.startswith(match)
               and el.state in START_STATES]

    return job_arr


async def submit_job(ctx, script=None):
    global _jobs

    max_submit_sleep = args.max_stagger
    sleep_for = random.randint(0, max_submit_sleep)
    logging.debug("Sleeping for {} seconds before submission".format(sleep_for))
    await asyncio.sleep(sleep_for)

    with _dict_lock:
        _jobs[ctx.dir] = Job(ctx.id, "SUBMITTED", False, False)

    threading.Thread(target=threaded_job, args=(ctx.dir, script)).start()
    return ctx.id

if __name__ == "__main__":
    pass
