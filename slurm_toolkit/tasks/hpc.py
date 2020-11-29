import asyncio
import logging
import re

from .utils import check_task, processing_task, execute_command

from pyslurm import job


_job_lock = asyncio.Lock()


@check_task
async def jobs(ctx, limit, match):
    # TODO: match with regex
    # TODO: Race condition present with last job submission
    async with _job_lock:
        job_names = [j['name'] for j in job().get().values()
                     if j['name'].startswith(match)
                     and j['job_state'] in ["COMPLETING", "PENDING", "RESV_DEL_HOLD", "RUNNING", "SUSPENDED"]]
        res = len(job_names) < int(limit)

        if not res:
            log = logging.warning
        else:
            log = logging.debug
        log("Jobs in action {} with limit {}".format(len(job_names), limit))
    return res


@processing_task
async def submit(ctx, script=None):
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')

    async with _job_lock:
        res = await execute_command("sbatch {}".format(script), cwd=ctx.dir)
        output = res.stdout.decode()

    sbatch_match = r_sbatch_id.match(output)
    if sbatch_match:
        job_id = sbatch_match.group(1)
        logging.info("Submitted job with ID {}".format(job_id))
        return job_id
    return None


@check_task
async def quota(ctx, atleast, mnt=None):
    # Command responds in 1k blocks
    path_arg = " -f " + mnt if mnt else ""
    quota_cmd = "quota -uw" + path_arg
    res = await execute_command(quota_cmd)
    quota_out = res.stdout

    try:
        fields = quota_out.splitlines()[-1].split()
        usage = int(fields[1])
        limit = int(fields[2])
        atleast = int(atleast)
    except (IndexError, TypeError) as e:
        logging.exception("Could not reliably determine quota information")
        return False

    res = (limit - usage) >= atleast

    if not res:
        logging.warning("Quota remaining {} is less than {}".format(limit - usage, atleast))
    return res

