import argparse
import logging
import os
import re

from .config import BatcherConfig
from .batcher import BatchExecutor
# TODO: logging and parse_args should be in utils
from .utils import Arguments, background_fork, setup_logging


def parse_indexes(argv):
    if re.match(r'^([0-9]+,)*[0-9]+$', argv):
        return [int(v) for v in argv.split(",")]
    raise argparse.ArgumentTypeError("{} is not a CSV delimited integer list of indexes".format(argv))


def parse_args():
    a = argparse.ArgumentParser()

    a.add_argument("-n", "--no-daemon", help="Do not daemon", default=True, action="store_true")

    # TODO: Need to validate the argument selections/group certain commands
    a.add_argument("-v", "--verbose", default=False, action="store_true")
    a.add_argument("-c", "--no-checks", default=False, action="store_true")
    a.add_argument("-s", "--no-submission", default=False, action="store_true")
    a.add_argument("-p", "--pickup", help="Continue a previous set of runs, for example when previously failed",
                   default=False, action="store_true")
    a.add_argument("-k", "--skips", help="Number of run entries to skip", default=0, type=int)
    a.add_argument("-i", "--indexes", help="Specify which indexes to run", type=parse_indexes)
    a.add_argument("-ct", "--check-timeout", default=10, type=int)
    a.add_argument("-st", "--submit-timeout", default=10, type=int)
    a.add_argument("-rt", "--running-timeout", default=10, type=int)
    a.add_argument("-et", "--error-timeout", default=120, type=int)
    a.add_argument("configuration")
    # Prefer retaining immutable Arguments() by not using the instance as a namespace
    return Arguments(**vars(a.parse_args()))


def main():
    args = parse_args()

    if not args.no_daemon:
        background_fork(True)

    setup_logging("{}".format(os.path.basename(args.configuration)),
                              verbose=args.verbose)

    logging.info("HPC Batching Tool")
    config = BatcherConfig(args.configuration)
    BatchExecutor(config).run()
