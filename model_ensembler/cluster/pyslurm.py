import asyncio
import collections
import logging
import os

from model_ensembler.tasks.utils import execute_command

# FIXME: bring underlying operations replacing pyslurm under cluster from
#  tasks.hpc
job_lock = asyncio.Lock()

# TODO: Generic across package
Job = collections.namedtuple("Job", ["name", "state", "started", "finished"])


async def find_id(job_id):
    """Method to find SLURM job by ID

    This method provides an interface to the squeue SLURM queue utility to
    identify a job and return it along with it's state

    Args:
        job_id (int): SLURM job identifier

    Returns:
        jobs (list): job objects including name and state
    """
    res = False

    # TODO: deadlocks submit
    #async with job_lock:
    job = None

    while not job:
        try:
            res = await execute_command("scontrol show job {} -o".
                                        format(job_id))
            output = res.stdout.decode()
        except Exception as e:
            logging.warning("Could not retrieve list: {}".format(e))
        else:
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
