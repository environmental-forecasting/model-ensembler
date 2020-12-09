import argparse
import logging

from .config import BatcherConfig
from .batcher import BatchExecutor
# TODO: logging and parse_args should be in utils
from .utils import Arguments


def parse_args():
    a = argparse.ArgumentParser()
    a.add_argument("-v", "--verbose", default=False, action="store_true")
    a.add_argument("-c", "--nochecks", default=False, action="store_true")
    a.add_argument("-s", "--nosubmission", default=False, action="store_true")
    a.add_argument("-p", "--pickup", help="Continue a previous set of runs, for example when previously failed",
                   default=False, action="store_true")
    a.add_argument("-ct", "--check-timeout", default=10, type=int)
    a.add_argument("-st", "--submit-timeout", default=10, type=int)
    a.add_argument("-rt", "--running-timeout", default=10, type=int)
    a.add_argument("configuration")
    # Prefer retaining immutable Arguments() by not using the instance as a namespace
    return Arguments(**vars(a.parse_args()))


def main():
    logging.getLogger().setLevel(logging.INFO)
    logging.info("HPC Batching Tool")

    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    config = BatcherConfig(args.configuration)
    BatchExecutor(config).run()
