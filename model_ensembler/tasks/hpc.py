import importlib
import logging

from model_ensembler.tasks.utils import \
    check_task, processing_task, execute_command

# TODO: dynamic imports need to take place here
cluster = None


def init_hpc_backend(backend):
    """ Initialise cluster backend to use.

    Args:
        backend (str): Cluster backed to use.

    Raises:
        ImportError/ModuleNotFoundError: If cluster backend cannot be imported.
    """
    global cluster

    logging.info("Importing {}".format(backend))
    try:
        cluster = importlib.import_module(backend)
    except (ImportError, ModuleNotFoundError) as e:
        logging.exception("Couldn't dynamically import cluster backend")
        raise e


"""HPC tasks

This module contains HPC related task methods
"""


async def find_id(job_id):
    return await cluster.find_id(job_id)


@check_task
async def jobs(ctx, limit, match):
    """Check: Assert whether number of jobs in SLURM is under limit.

    Args:
        ctx (object): Contextual configuration.
        limit (int): Number of jobs to check for.
        match (str): Prefix to match jobs by.

    Returns:
        (bool): True if number of jobs is less than limit, otherwise false.
    """

    # TODO: match with regex
    async with cluster.job_lock:
        job_list = await cluster.current_jobs(ctx, match)
        res = len(job_list) < int(limit)

        logging.debug("Jobs in action {} with limit {}".format(
            len(job_list), limit))

    return res


@processing_task
async def submit(ctx, script=None):
    """Process: Submit a new job to SLURM.

    Args:
        ctx (object): Contextual configuration.
        script (str, optional): Slurm submission script for sbatch.

    Returns:
        (int): Job identifier.
    """

    # TODO: check this as an optional argument avoids run submission
    #  as intended
    if script:
        async with cluster.job_lock:
            await cluster.submit_job(ctx, script)

    return None


@check_task
async def quota(ctx, atleast, mnt=None):
    """Check: Make sure quota is sufficient.

    Args:
        ctx (object): Contextual configuration.
        atleast (int): Amount in kB.
        mnt (str, optional): Path for mount to check quota on if explicitly
                            required.

    Returns:
        (bool): True if available space is less than atleast, false otherwise.

    Raises:
        IndexError/TypeError: If quota cannot be determined.
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
