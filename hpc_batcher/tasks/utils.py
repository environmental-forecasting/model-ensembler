import functools
import logging
import shlex
import subprocess

from hpc_batcher.utils import Arguments


def batch_task(func=None, notcheck=False):
    if not func:
        new = functools.partial(batch_task, notcheck=notcheck)
        return new

    @functools.wraps(func)
    def new_func(run, **kwargs):
        # TODO: we need to consolidate arguments into the configuration and make these contextually
        # available to all actions
        config = Arguments()

        for k, v in kwargs.items():
            try:
                # TODO: Problem if we call the job run.sh
                if type(v) == str and v.startswith("run."):
                    nom = v.split(".")[1]
                    kwargs[k] = run[nom]
            finally:
                logging.debug("Calling with {} = {}".format(
                    k, kwargs[k])
                )

        if config.nochecks and not notcheck:
            logging.info("Skipping checks for {}".format(func.__name__))
            return True
        return func(run, **kwargs)
    return new_func


def execute_command(cmd):
    logging.info("Checking command {0}".format(cmd))

    ret = subprocess.run(shlex.split(cmd),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         text=True)

    if ret.returncode != 0:
        logging.warning("Command returned: {}".format(ret.returncode))
        return ret
    else:
        logging.info("Check return output: {0}".format(ret))
    return ret
