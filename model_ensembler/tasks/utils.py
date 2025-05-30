import asyncio
import functools
import inspect
import logging
import os
import types

from datetime import datetime

from model_ensembler.utils import Arguments

"""Task utilities

This module contains implementation and functionality relating generally to
tasks
"""


def flight_task(func, check=True):
    """Decorator for making func as a task, providing context preprocessing.

    Args:
        func (callable): Callable to wrap with context.
        check (bool, optional): Determine whether the func is to be treated
            as a check or another type of action (checks can be skipped).

    Returns:
        (func): The wrapped function that can process the context provided
            appropriately.
    """

    @functools.wraps(func)
    def new_func(ctx, *args, **kwargs):
        config = Arguments()

        for k, v in kwargs.items():
            try:
                if type(v) == str and str(v).startswith("run."):
                    nom = v.split(".")[1]
                    kwargs[k] = getattr(ctx, nom)
            finally:
                logging.debug("Calling with {} = {}".format(
                    k, kwargs[k])
                )

        # FIXME: context magic for execute_command calls below,
        #  not necessarily the best manner to achieve this as it would be
        #  better handled via the decorator
        if hasattr(ctx, 'dir') and 'cwd' in inspect.signature(func).parameters:
            kwargs['cwd'] = ctx.dir

        if config.no_checks and check:
            logging.info("Skipping checks for {}".format(func.__name__))
            return True
        return func(ctx, *args, **kwargs)

    new_func.check = check
    return new_func


check_task = functools.partial(flight_task, check=True)
processing_task = functools.partial(flight_task, check=False)


async def execute_command(cmd, cwd=None, log=False, shell=None):
    """Standard handling for calling external command.

    Args:
        cmd (str): The relative path of the command being called to cwd.
        cwd (str, optional): The current working directory to call the cmd
            from, passed to subprocess.
        log (bool, optional): If true, output stdout/stderr to logfile in cwd.
        shell (str, optional): Which shell to ask subprocess to invoke when
            processing the command, will default to bash internally.

    Returns:
        (object): Namespace containing the returncode, stdout and stderr from
            the process that was invoked.
    """

    logging.debug("Executing command {0}, cwd {1}".
                  format(cmd, cwd if cwd else "unset"))

    start_dt = datetime.now()

    args = Arguments()
    shell = args.shell if not shell else shell

    proc = await asyncio.create_subprocess_shell(
        cmd,
        executable=shell,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=cwd)

    (stdout, stderr) = await proc.communicate()
    await proc.wait()

    if log and stdout:
        log_name = "execute_command.{}.log".\
            format(start_dt.strftime("%H%M%S.%f"))

        if cwd:
            log_name = os.path.join(cwd, log_name)

        with open(log_name, "w") as fh:
            fh.write(stdout.decode())

        logging.info("Command log written to {}".format(log_name))

    ret = types.SimpleNamespace(
        returncode=proc.returncode, stdout=stdout, stderr=stderr)

    if ret.returncode != 0:
        logging.warning("Command returned err: {}".format(ret.stderr))
        return ret
    else:
        logging.debug("Command successful")
    return ret
