import logging
import os
import shutil

from .exceptions import FailureNotToleratedError
from .utils import check_task, processing_task, execute_command

"""System tasks

This module contains all methods for system related tasks
"""


@check_task
async def check(ctx, cmd, cwd=None, log=False, fail=False, shell=None):
    """Check: Call arbitrary command as a check.

    Args:
        ctx (object): Contextual configuration.
        cmd (str): See ``utils.execute_command``.
        cwd (str, optional): See ``utils.execute_command``.
        log (bool, optional): See ``utils.execute_command``.
        fail (bool, optional): If true, then the check returning nonzero will
            raise an error rather than return false, meaning run abandonment
            rather than recheck will take place.
        shell (str, optional):  See ``utils.execute_command``.

    Returns:
        (bool): True if return code is zero, false otherwise.

    Raises:
        FailureNotToleratedError: Error when fail is true and the check
            returns a nonzero code.
    """

    logging.info("Running check: {}".format(cmd))

    res = await execute_command(cmd, cwd, log, shell)
    logging.debug("Check return code {}".format(res.returncode))

    if res.returncode == 0:
        return True

    if fail:
        raise FailureNotToleratedError("Check failed and it is not tolerable")
    return False


@processing_task
async def execute(ctx, cmd, cwd=None, log=False, shell=None):
    """Process: Call arbitrary command as a processing task.

    Args:
        ctx (object): Contextual configuration.
        cmd (str):  See ``utils.execute_command``.
        cwd (str, optional): See ``utils.execute_command``.
        log (bool, optional): See ``utils.execute_command``.
        shell (str, optional): See ``utils.execute_command``.

    Returns:
        (bool): True if return code is zero, false otherwise.
    """
    logging.info("Running command: {}".format(cmd))

    res = await execute_command(cmd, cwd, log, shell)
    if res.returncode == 0:
        return True
    return False


# TODO: Context identification. WE MUST HAVE ID
@processing_task
async def move(ctx, dest, include=None, exclude=None, cwd=None):
    """Process: rsync current working directory contents.

    Args:
        ctx (object): Contextual configuration.
        dest (str): Path to copy ctx.id named directory to.
        include (List[str], optional): rsync include specifiers.
        exclude (List[str], optional): rsync exclude specifiers, defaults to
            "*" when calling rsync if include specifiers are given and no
            exclude specifiers are provided.
        cwd (str, optional): See ``utils.execute_command``.

    Returns:
        (bool): true if return code is zero, false otherwise.

    Raises:
        RuntimeError: If did not provide necessary context attribute for using
            this processing task.
    """

    if not hasattr(ctx, "id"):
        raise RuntimeError("No ID available for move")

    # TODO: Type checking
    include = [] if not include else include
    exclude = ["*"] if not exclude and include else []
    dest = os.path.join(dest, ctx.id)

    liststr = " ".join(["--include=\"{}\"".
                       format(i.strip("\"")) for i in include]) + " " + \
        " ".join(["--exclude=\"{}\"".
                 format(e.strip("\"")) for e in exclude])

    cmd = "rsync -aXE {} ./ {}/".format(liststr, dest)
    logging.info(cmd)

    res = await execute_command(cmd, cwd)
    if res.returncode == 0:
        return True
    return False


@processing_task
async def remove(ctx, directory=None):
    """Process: Remove directory using shutil.rmtree.

    Args:
        ctx (object): Contextual configuration.
        directory (str, optional): Specify the directory to remove, otherwise
            this will use the path specified by ctx.dir.

    Returns:
        (bool): True if return code is zero, false otherwise.

    Raises:
        OSError: If directory cannot be removed.
    """
    if not directory:
        directory = ctx.dir

    logging.info("Attempting to remove data on {}".format(directory))

    try:
        shutil.rmtree(directory)
    except OSError as e:
        logging.exception("Could not remove {}: {}".
                          format(directory, e.strerror))
        return False
    return True
