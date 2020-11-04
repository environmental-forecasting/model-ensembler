import logging
import shutil

from .utils import check_task, processing_task, execute_command


@check_task
def check(ctx, cmd):
    logging.info("Running check: {}".format(cmd))
    kwargs = {}

    if dir in ctx:
        kwargs['cwd'] = ctx.dir
        
    if execute_command(cmd, **kwargs).returncode == 0:
        return True
    return False


@processing_task
def execute(ctx, cmd):
    logging.info("Running command: {}".format(cmd))
    kwargs = {}

    if dir in ctx:
        kwargs['cwd'] = ctx.dir

    if execute_command(cmd, **kwargs).returncode == 0:
        return True
    return False


# TODO: This is a good example of a task to be run at the batch level, as well as at the run level...
@processing_task
def remove(ctx, dir):
    logging.info("Attempting to remove data on {}".format(dir))

    try:
        shutil.rmtree(dir)
    except OSError as e:
        logging.exception("Could not remove {}: {}".format(dir, e.strerror))
        return False
    return True
