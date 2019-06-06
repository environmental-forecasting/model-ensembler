import logging
import os

from hpc_batcher.tasks.utils import batch_task, execute_command


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


@batch_task(notcheck=True)
def getdata(run, source, dest, ssh):
    return do_rsync("rsync -rtzD {2}:{0} {1}", source, dest, ssh)


@batch_task
def putdata(run, source, dest, ssh):
    return do_rsync("rsync -rtzD {0} {2}:{1}", source, dest, ssh)


@batch_task
def removedata(run, dir, nomoreruns=False):
    # TODO: Batch availability
    logging.warning("Need to implement batch scoping for removedata")
    return True

