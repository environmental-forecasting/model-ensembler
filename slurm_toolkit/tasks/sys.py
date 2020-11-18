import logging
import shutil

from .utils import check_task, processing_task, execute_command


@check_task
async def check(ctx, cmd, cwd=None, log=False):
    logging.info("Running check: {}".format(cmd))

    res = await execute_command(cmd, cwd, log)
    if res.returncode == 0:
        return True
    return False


@processing_task
async def execute(ctx, cmd, cwd=None, log=False):
    logging.info("Running command: {}".format(cmd))

    res = await execute_command(cmd, cwd, log)
    if res.returncode == 0:
        return True
    return False


# TODO: This is a good example of a task to be run at the batch level, as well as at the run level...
@processing_task
async def remove(ctx, dir):
    raise NotImplementedError("remove not implemented")
#    logging.info("Attempting to remove data on {}".format(dir))
#
#    try:
#        shutil.rmtree(dir)
#    except OSError as e:
#        logging.exception("Could not remove {}: {}".format(dir, e.strerror))
#        return False
#    return True
