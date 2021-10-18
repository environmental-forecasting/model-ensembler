import asyncio
import collections
import logging
import os
import re

from pprint import pformat

from model_ensembler.tasks.utils import execute_command
from model_ensembler.cluster import Job, job_lock

START_STATES = ("COMPLETING", "PENDING", "RESV_DEL_HOLD", "RUNNING",
                "SUSPENDED", "CONFIGURING", "REQUEUE_FED", "REQUEUE_HOLD",
                "REQUEUED", "RESIZING", "REVOKED", "SIGNALED", "STOPPED")
FINISH_STATES = ("COMPLETED", "FAILED", "CANCELLED", "OUT_OF_MEMORY",
                 "DEADLINE", "NODE_FAIL", "PREEMPTED", "TIMEOUT")


async def find_id(job_id):
    """Method to find SLURM job by ID

    This method provides an interface to the squeue SLURM queue utility to
    identify a job and return it along with it's state

    Args:
        job_id (int): SLURM job identifier

    Returns:
        jobs (list): job objects including name and state
    """
    job = None

    while not job:
        try:
            res = await execute_command("scontrol show job {} -o".
                                        format(job_id))
            output = res.stdout.decode()
        except Exception as e:
            logging.warning("Could not retrieve list: {}".format(e))
        else:
            # FIXME: scontrol won't find the job once departed from cluster
            fields = output.split()
            job = Job(
                # TODO: ewwwwwwww stop being so grim and make this nicer
                name=[v.split("=")[1] for v in fields
                      if v.split("=")[0] == "JobName"][0],
                state=[v.split("=")[1] for v in fields
                       if v.split("=")[0] == "JobState"][0],
                started=[v.split("=")[1] for v in fields
                         if v.split("=")[0] == "StartTime"][0] == "Unknown",
                finished=[v.split("=")[1] for v in fields
                          if v.split("=")[0] == "EndTime"][0] == "Unknown"
            )

            logging.debug("SLURM find result name: {}".format(job.name))
    return job


async def current_jobs(ctx, match):
    filtered_jobs = None

    # Ensure we account for empty lists
    while not filtered_jobs and filtered_jobs is None:
        try:
            res = await execute_command("squeue -o \"%j,%T\" -h -p {}".
                                        format(ctx.cluster),
                                        cwd=ctx.dir)
            output = res.stdout.decode()
        except Exception as e:
            logging.warning("Could not retrieve list: {}".format(e))
        else:
            jobs = []
            for line in output.split():
                fields = line.strip().split(",")
                jobs.append({"name": fields[0], "job_state": fields[1]})

            filtered_jobs = [{"name": j['name'], "state": j["job_state"]}
                         for j in jobs
                         if j['name'].startswith(match)
                         and j['job_state'] in START_STATES]

            logging.debug("SLURM JOBS result: {}".
                          format(pformat(filtered_jobs)))

    return filtered_jobs


async def submit_job(ctx, script=None):
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')
    res = await execute_command("sbatch {}".format(script),
                                cwd=ctx.dir)
    output = res.stdout.decode()

    sbatch_match = r_sbatch_id.match(output)
    if sbatch_match:
        job_id = sbatch_match.group(1)
        logging.info("Submitted job with ID {}".format(job_id))

        return int(job_id)
    return None
