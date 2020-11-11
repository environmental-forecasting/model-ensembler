import logging
import shutil

from .utils import check_task, processing_task, execute_command


@check_task
async def check(ctx, cmd, **kwargs):
    logging.info("Running check: {}".format(cmd))

    res = await execute_command(cmd, **kwargs)
    if res.returncode == 0:
        return True
    return False


@processing_task
async def execute(ctx, cmd, **kwargs):
    logging.info("Running command: {}".format(cmd))

    res = await execute_command(cmd, **kwargs)
    if res.returncode == 0:
        return True
    return False


# TODO: This is a good example of a task to be run at the batch level, as well as at the run level...
@processing_task
async def remove(ctx, dir):
    logging.info("Attempting to remove data on {}".format(dir))

    try:
        shutil.rmtree(dir)
    except OSError as e:
        logging.exception("Could not remove {}: {}".format(dir, e.strerror))
        return False
    return True
