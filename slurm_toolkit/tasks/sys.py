import logging

from .utils import execute_command, batch_task


@batch_task
def check(run, cmdstr):
    logging.info("Running check: {}".format(cmdstr))

    if execute_command(cmdstr, cwd=run.dir).returncode == 0:
        return True
    return False


@batch_task(check=False)
def execute(run, cmdstr):
    logging.info("Running command: {}".format(cmdstr))

    if execute_command(cmdstr, cwd=run.dir).returncode == 0:
        return True
    return False
