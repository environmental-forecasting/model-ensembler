import logging
import os

from hpc_batcher.tasks.utils import execute_command, batch_task


@batch_task
def check(run, cmdstr):
    # TODO: Improve the handling
    if not cmdstr.startswith(os.sep):
        cmdstr = os.path.join(run.dir, cmdstr)

    logging.info("Running check: {}".format(cmdstr))

    if execute_command(cmdstr).returncode == 0:
        return True
    return False


@batch_task(check=False)
def execute(run, cmdstr):
    if not cmdstr.startswith(os.sep):
        cmdstr = os.path.join(run.dir, cmdstr)

    logging.info("Running command: {}".format(cmdstr))

    if execute_command(cmdstr).returncode == 0:
        return True
    return False
