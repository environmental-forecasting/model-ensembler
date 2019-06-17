import logging
import os
import shutil

from hpc_batcher.tasks.utils import batch_task, execute_command


# TODO: Better rsync handling wrt logging, rsync specs and validation
def do_rsync(spec, source, dest, ssh):
    if not dest.endswith(os.sep):
        dest += os.sep

    cmd = spec.format(
        source, dest, ssh
    )

    logging.info("Running getdata using {}".format(cmd))
    res = execute_command(cmd)

    if res.returncode == 0:
        return True
    return False


@batch_task(check=False)
def getdata(run, source, dest, ssh="", spec=""):
    basecmd = "rsync -rptgoDXEL {} ".format(spec)
    cmd = basecmd + "{0} {1}"
    if len(ssh):
        cmd = basecmd + "{2}:{0} {1}"

    logging.info("Running getdata using {}".format(cmd))
    return do_rsync(cmd, source, dest, ssh)


@batch_task(check=False)
def putdata(run, source, dest, ssh="", spec=""):
    basecmd = "rsync -rptgoDXEL {} ".format(spec)
    cmd = basecmd + "{0} {1}"
    if len(ssh):
        cmd = basecmd + "{0} {2}:{1}"

    logging.info("Running putdata using {}".format(cmd))
    return do_rsync(cmd, source, dest, ssh)


@batch_task(check=False)
def removedata(run, dir, nomoreruns=False):
    if nomoreruns:
        raise RuntimeError("nomoreruns is not implemented yet, need Executor scoping")

    logging.info("Attempting to remove data on {}".format(dir))

    try:
        shutil.rmtree(dir)
    except OSError as e:
        logging.exception("Could not remove {}: {}".format(dir, e.strerror))
        return False
    return True

