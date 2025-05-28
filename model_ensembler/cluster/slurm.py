import asyncio
import logging
import random
import re

from pprint import pformat

from model_ensembler.tasks.utils import execute_command
from model_ensembler.cluster import Job, job_lock
from model_ensembler.utils import Arguments

START_STATES = ("COMPLETING", "PENDING", "RESV_DEL_HOLD", "RUNNING",
                "SUSPENDED", "CONFIGURING", "REQUEUE_FED", "REQUEUE_HOLD",
                "REQUEUED", "RESIZING", "REVOKED", "SIGNALED", "STOPPED",
                "FAILED")
FINISH_STATES = ("COMPLETED", "FAILED", "CANCELLED", "OUT_OF_MEMORY",
                 "DEADLINE", "NODE_FAIL", "PREEMPTED", "TIMEOUT")


async def find_id(job_id):
    """Method to find SLURM job by ID.

    This method provides an interface to the squeue SLURM queue utility to
    identify a job and return it along with it's state.

    Args:
        job_id (int): SLURM job identifier.

    Returns:
        jobs (list): Job objects including name and state.

    Raises:
        ValueError: If cannot retrieve job from list.
    """
    job = None
    args = Arguments()

    while not job:
        try:
            res = await execute_command("sacct -XnP -j {} "
                                        "-o jobname,state,start,end".
                                        format(job_id))
            output = res.stdout.decode().strip()
            (name, state, started, finished) = output.split("|")
        except ValueError:
            logging.debug("Could not retrieve job from list")
            await asyncio.sleep(args.check_timeout)
        else:
            job = Job(
                name=name,
                state=state.split()[0],
                started=started == "Unknown",
                finished=finished == "Unknown"
            )

    logging.debug("SLURM find result name: {}".format(job.name))
    return job


async def current_jobs(ctx, match):
    """Method to get list of current jobs

    Args:
        ctx (object): Context object for retrieving configuration.
        match (str): Jobs to match the job list with.

    Returns:
        (list): Filtered jobs.
    """
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
    """Method to submit jobs to SLURM.

    Args:
        ctx (object): Context object for retrieving configuration.
        script (str): Script name to submit.

    Returns:
        (int): Job ID.
    """
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')
    args = Arguments()

    # Don't smash the scheduler immediately, it appears to have the potential
    # to cause problems.
    sleep_for = random.randint(0, args.max_stagger)
    logging.debug(
        "Sleeping for {} seconds before submission".format(sleep_for))
    await asyncio.sleep(sleep_for)
    res = await execute_command("sbatch --no-requeue {}".format(script),
                                cwd=ctx.dir)
    output = res.stdout.decode()

    sbatch_match = r_sbatch_id.match(output)
    if sbatch_match:
        job_id = sbatch_match.group(1)
        logging.info("Submitted job with ID {}".format(job_id))

        return int(job_id)
    return None
