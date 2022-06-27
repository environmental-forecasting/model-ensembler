import asyncio
import logging
import random
import re

from pprint import pformat

from model_ensembler.tasks.utils import execute_command
from model_ensembler.cluster import Job
from model_ensembler.utils import Arguments

from model_ensembler.cluster.slurm import \
    START_STATES, FINISH_STATES, find_id, current_jobs


async def submit_job(ctx, script=None):
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')
    args = Arguments()

    # Don't smash the scheduler immediately, it appears to have the potential
    # to cause problems. 
    sleep_for = random.randint(0, args.max_stagger)
    logging.debug("Sleeping for {} seconds before submission".format(sleep_for))
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
