import logging
import os
import shutil

from .utils import check_task, processing_task, execute_command


@check_task
async def check(ctx, cmd, cwd=None, log=False, fail=False, shell=None):
    logging.info("Running check: {}".format(cmd))

    res = await execute_command(cmd, cwd, log, shell)
    if res.returncode == 0:
        return True

    if fail:
        raise FailureNotToleratedError("Check failed and it is not tolerable")
    return False


@processing_task
async def execute(ctx, cmd, cwd=None, log=False, shell=None):
    logging.info("Running command: {}".format(cmd))

    res = await execute_command(cmd, cwd, log, shell)
    if res.returncode == 0:
        return True
    return False


# TODO: Context identification. WE MUST HAVE ID
@processing_task
async def move(ctx, dest, include=None, exclude=None, cwd=None):
    if not hasattr(ctx, "id"):
        raise RuntimeError("No ID available for move")

    # TODO: Type checking
    include = [] if not include else include
    exclude = ["*"] if not exclude and include else [] if exclude else exclude
    dest = os.path.join(dest, ctx.id)

    liststr = " ".join(["--include=\"{}\"".format(i.strip("\"")) for i in include]) + " " + \
        " ".join(["--exclude=\"{}\"".format(e.strip("\"")) for e in exclude])
    cmd = "rsync -aXE {} ./ {}/".format(liststr, dest)
    logging.info(cmd)

    res = await execute_command(cmd, cwd)
    if res.returncode == 0:
        return True
    return False


@processing_task
async def remove(ctx, directory=None):
    if not directory:
        directory = ctx.dir

    logging.info("Attempting to remove data on {}".format(directory))

    try:
        shutil.rmtree(directory)
    except OSError as e:
        logging.exception("Could not remove {}: {}".format(directory, e.strerror))
        return False
    return True


class FailureNotToleratedError(RuntimeError):
    pass
