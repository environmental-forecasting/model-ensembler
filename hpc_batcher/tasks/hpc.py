import logging
import os
import re
import time

# TODO: from fabric import task

from hpc_batcher.tasks.utils import execute_command, batch_task

from pyslurm import job


@batch_task(check=False)
def submit(run, script=None):
    r_sbatch_id = re.compile(r'Submitted batch job (\d+)$')
    orig = os.getcwd()
    os.chdir(run.dir)
    output = execute_command("sbatch {}".format(script)).stdout
    os.chdir(orig)

    sbatch_match = r_sbatch_id.match(output)
    if sbatch_match:
        job_id = sbatch_match.group(1)
        logging.info("Submitted job with ID {}".format(job_id))
        return job_id
    return None


@batch_task
def quota(run, atleast, mnt):
    # Command responds in 1k blocks
    quota_cmd = " ".join(["quota -uw -f", mnt])
    quota_out = execute_command(quota_cmd).stdout

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


@batch_task
def jobs(run, limit, match):
    # TODO: match needs to be a regex but suffering problems with that currently
    job_names = [j['name'] for j in job().get().values()
                 if j['name'].startswith(match)
                 and j['job_state'] == 'RUNNING']
    res = len(job_names) < int(limit)

    if not res:
        log = logging.warning
    else:
        log = logging.debug
    log("Jobs in action {} with limit {}".format(len(job_names), limit))
    return res
