import asyncio
import logging
import re

from model_ensembler.cluster.pyslurm import job_lock, find_id

from model_ensembler.tasks.utils import \
    check_task, processing_task, execute_command
from model_ensembler.utils import Arguments

from pprint import pformat

"""HPC tasks

This module contains HPC related task methods
"""


@check_task
async def jobs(ctx, limit, match):
    """Check: Assert whether number of jobs in SLURM is under limit

    Args:
        ctx (object): contextual configuration
        limit (int): number of jobs to check for
        match (str): prefix to match jobs by

    Returns:
        bool: true if number of jobs is less than limit, otherwise false
    """
    res = False

    # TODO: match with regex
    async with job_lock:
        jobs = None

        while not jobs:
            try:
                res = await execute_command("squeue -o \"%j,%T\" -h",
                                            cwd=ctx.dir)
                output = res.stdout.decode()
            except Exception as e:
                logging.warning("Could not retrieve list: {}".format(e))
            else:
                jobs = []
                for line in output.split():
                    fields = line.strip().split(",")
                    jobs.append({"name": fields[0], "job_state": fields[1]})

                job_names = [{"name": j['name'], "state": j["job_state"]}
                             for j in jobs
                             if j['name'].startswith(match)
                             and j['job_state'] in [
                                 "COMPLETING", "PENDING", "RESV_DEL_HOLD",
                                 "RUNNING", "SUSPENDED"]]

                logging.debug("SLURM JOBS result: {}".format(pformat(job_names)))

                res = len(job_names) < int(limit)

                logging.debug("Jobs in action {} with limit {}".format(
                    len(job_names), limit))
    return res


@processing_task
async def submit(ctx, script=None):
    """Process: Submit a new job to SLURM

    Args:
        ctx (object): contextual configuration
        script (str, optional): slurm submission script for sbatch

    Returns:
        int: job identifier
    """
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')
    args = Arguments()

    # TODO: check this as an optional argument avoids run submission
    #  as intended
    if script:
        async with job_lock:
            res = await execute_command("sbatch {}".format(script),
                                        cwd=ctx.dir)
            output = res.stdout.decode()

            sbatch_match = r_sbatch_id.match(output)
            if sbatch_match:
                job_id = sbatch_match.group(1)
                logging.info("Submitted job with ID {}".format(job_id))

                job_results = find_id(int(job_id))
                while len(job_results) != 1:
                    logging.warning("Job {} has not appeared in {} queue "
                                    "results yet, waiting for appearance".
                                    format(job_id, len(job_results)))
                    await asyncio.sleep(args.submit_timeout)
                    job_results = find_id(int(job_id))

                return job_id
    return None


@check_task
async def quota(ctx, atleast, mnt=None):
    """Check: Make sure quota is sufficient

    Args:
        ctx (object): contextual configuration
        atleast (int): amount in kB
        mnt (str, optional): path for mount to check quota on if explicitly
        required

    Returns:
        bool: true if available space is less than atleast, false otherwise
    """

    # Command responds in 1k blocks
    path_arg = " -f " + mnt if mnt else ""
    quota_cmd = "quota -uw" + path_arg
    res = await execute_command(quota_cmd)
    quota_out = res.stdout.decode()

    try:
        fields = quota_out.splitlines()[-1].split()
        usage = int(fields[1])
        limit = int(fields[2])
        atleast = int(atleast)
    except (IndexError, TypeError):
        logging.exception("Could not reliably determine quota information")
        return False

    res = (limit - usage) >= atleast

    if not res:
        logging.warning("Quota remaining {} is less than {}".
                        format(limit - usage, atleast))
    return res
