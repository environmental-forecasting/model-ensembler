import asyncio
import collections
import logging
import os

from model_ensembler.tasks.utils import execute_command

# FIXME: bring underlying operations replacing pyslurm under cluster from
#  tasks.hpc
job_lock = asyncio.Lock()

# TODO: Generic across package
Job = collections.namedtuple("Job", ["name", "state"])


async def find_id(job_id):
    res = False

    # TODO: match with regex
    async with job_lock:
        jobs = None

        while not jobs:
            try:
                res = await execute_command("squeue -o \"%j,%T\" -h")
                output = res.stdout.decode()
            except Exception as e:
                logging.warning("Could not retrieve list: {}".format(e))
            else:
                jobs = []
                for line in output.split():
                    fields = line.strip().split(",")
                    jobs.append(Job(
                        name=fields[0],
                        state=fields[1]
                    ))

                logging.debug("SLURM find result: {}".format(len(jobs)))
    return res
