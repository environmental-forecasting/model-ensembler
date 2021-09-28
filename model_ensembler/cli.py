import argparse
import logging
import os
import re

from .config import EnsembleConfig
from .batcher import BatchExecutor
# TODO: logging and parse_args should be in utils
from .utils import Arguments, background_fork, setup_logging

"""CLI entry module

This module contains all package entry_points
"""


def parse_indexes(argv):
    """ Method for ensuring a CSV string of integers

    Returns:
        list: List of integer values
    """
    if re.match(r'^([0-9]+,)*[0-9]+$', argv):
        return [int(v) for v in argv.split(",")]
    raise argparse.ArgumentTypeError("{} is not a CSV delimited integer list "
                                     "of indexes".format(argv))


def parse_args():
    """Parse command line parameters

    Returns:
        Arguments: The immutable instance from ``.utils``
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--no-daemon",
                        help="Do not daemon", default=True,
                        action="store_true")

    # TODO: Need to validate the argument selections/group certain commands
    parser.add_argument("-v", "--verbose",
                        help="Log verbosely", default=False,
                        action="store_true")
    parser.add_argument("-c", "--no-checks",
                        help="Do not run check commands", default=False,
                        action="store_true")
    parser.add_argument("-s", "--no-submission",
                        help="Do not try to submit job, just log the step",
                        default=False, action="store_true")
    parser.add_argument("-p", "--pickup",
                        help="Continue a previous set of runs by picking up "
                        "existing directories rather, than assuming to create "
                        "them; for example if ensemble has previously failed",
                        default=False, action="store_true")

    # FIXME: These should not be applied in multi-batch ensembles
    parser.add_argument("-k", "--skips",
                        help="Number of run entries to skip", default=0,
                        type=int)
    parser.add_argument("-i", "--indexes",
                        help="Specify which indexes to run",
                        type=parse_indexes)
    parser.add_argument("-ct", "--check-timeout", default=10, type=int)
    parser.add_argument("-st", "--submit-timeout", default=10, type=int)
    parser.add_argument("-rt", "--running-timeout", default=10, type=int)
    parser.add_argument("-et", "--error-timeout", default=120, type=int)

    parser.add_argument("configuration")
    parser.add_argument("backend", default="slurm", required=False,
                        choices=("slurm", "dummy"))

    # Prefer retaining immutable Arguments()
    # by not using the instance as a namespace
    return Arguments(**vars(parser.parse_args()))


def main():
    """CLI entry point
    """
    args = parse_args()

    if not args.no_daemon:
        background_fork(True)

    setup_logging("{}".format(os.path.basename(args.configuration)),
                  verbose=args.verbose)

    logging.info("Model Ensemble Runner")
    config = EnsembleConfig(args.configuration)
    BatchExecutor(config, args.backend).run()
