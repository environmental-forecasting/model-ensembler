import asyncio
import functools
import logging
import os
import shlex
import sys
import types

from datetime import datetime

from ..utils import Arguments


def flight_task(func, check=True):
    @functools.wraps(func)
    def new_func(ctx, *args, **kwargs):
        config = Arguments()

        for k, v in kwargs.items():
            try:
                if type(v) == str and v.startswith("run."):
                    nom = v.split(".")[1]
                    kwargs[k] = getattr(ctx, nom)
            finally:
                logging.debug("Calling with {} = {}".format(
                    k, kwargs[k])
                )

        # A bit of context magic for execute_command calls below (TODO: better way with context stack/proxy)
        if hasattr(ctx, 'dir'):
            kwargs['cwd'] = ctx.dir

        if config.nochecks and check:
            logging.info("Skipping checks for {}".format(func.__name__))
            return True
        return func(ctx, *args, **kwargs)

    new_func.check = check
    return new_func


check_task = functools.partial(flight_task, check=True)
processing_task = functools.partial(flight_task, check=False)


async def execute_command(cmd, cwd=None, log=False):
    logging.info("Executing command {0}, cwd {1}".format(cmd, cwd if cwd else "unset"))

    start_dt = datetime.now()

    proc = await asyncio.create_subprocess_shell(cmd,
                                                 executable='/usr/bin/bash',
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.STDOUT,
                                                 cwd=cwd)

    (stdout, stderr) = await proc.communicate()
    await proc.wait()

    if log and stdout:
        log_name = "execute_command.{}.log".format(start_dt.strftime("%H%M%S.%f"))

        if cwd:
            log_name = os.path.join(cwd, log_name)

        with open(log_name, "w") as fh:
            fh.write(stdout.decode())

        logging.info("Command log written to {}".format(log_name))

    ret = types.SimpleNamespace(returncode=proc.returncode, stdout=stdout, stderr=stderr)
    logging.info(ret)

    if ret.returncode != 0:
        logging.warning("Command returned err: {}".format(ret.stderr))
        return ret
    else:
        logging.info("Command successful")
    return ret
