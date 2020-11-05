import functools
import logging
import os
import shlex
import subprocess

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


def execute_command(cmd, cwd=None):
    logging.info("Executing command {0}, cwd {1}".format(cmd, cwd if cwd else "unset"))
    logging.info("CWD: {}".format(os.getcwd()))

    ret = subprocess.run(shlex.split(cmd),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         cwd=cwd)

    if ret.returncode != 0:
        logging.warning("Command returned err {}: {}".format(ret.returncode, ret.stdout))
        return ret
    else:
        logging.info("Check return output: {}".format(ret.stdout))
    return ret
