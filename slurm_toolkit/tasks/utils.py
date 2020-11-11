import asyncio
import functools
import logging
import os
import shlex
import subprocess
import sys
import types

from datetime import datetime

from ..utils import Arguments


def flight_task(func, check=True):
    @functools.wraps(func)
    def new_func(run, *args, **kwargs):
        config = Arguments()

        for k, v in kwargs.items():
            try:
                if type(v) == str and v.startswith("run."):
                    nom = v.split(".")[1]
                    kwargs[k] = getattr(run, nom)
            finally:
                logging.debug("Calling with {} = {}".format(
                    k, kwargs[k])
                )

        if config.nochecks and check:
            logging.info("Skipping checks for {}".format(func.__name__))
            return True
        return func(run, *args, **kwargs)

    new_func.check = check
    return new_func


check_task = functools.partial(flight_task, check=True)
processing_task = functools.partial(flight_task, check=False)


async def execute_command(cmd, cwd=None, log=False):
    logging.info("Executing command {0}, cwd {1}".format(cmd, cwd if cwd else "unset"))
    # The asyncio loop has the cwd context of the loop, not of the chdir we've done. I think :-/
    cwd = os.getcwd() if not cwd else cwd

    start_dt = datetime.now()

    args = shlex.split(cmd)
    logging.debug(args)

    proc = await asyncio.create_subprocess_exec(*args,
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                cwd=cwd,
                                                encoding="utf8")

    (stdout, stderr) = await proc.communicate()

    if log and stdout:
        log_name = "execute_command.{}.log".format(start_dt.strftime("%H%M%S.%f"))

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
