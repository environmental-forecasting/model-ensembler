import argparse
import logging
import os
import re
import sys

from .config import EnsembleConfig
from .batcher import BatchExecutor
# TODO: logging and parse_args should be in utils
from .utils import Arguments, background_fork, setup_logging

"""CLI entry module

This module contains all package entry_points
"""


def parse_indexes(argv):
    """ Method for ensuring a CSV string of integers.

    Args:
        argv (list): expecting delimited integer list.

    Returns:
        (list): Matched integer values.

    Raises:
        argparse.ArgumentTypeError: If argv is not CSV delimited integer list.
    """
    if re.match(r'^([0-9]+,)*[0-9]+$', argv):
        return [int(v) for v in argv.split(",")]
    raise argparse.ArgumentTypeError("{} is not a CSV delimited integer list "
                                     "of indexes".format(argv))


def parse_extra_vars(arg):
    """ Method for processing extra var arguments.

    Args:
        arg (tuple): Collection of extra var arguments.

    Returns:
        (tuple): Name and value for the argument to be overridden.
    Raises:
        argparse.ArgumentTypeError: If arguments do not match.
    """

    arg_match = re.match(r'^([^=]+)=(.+)$', arg)
    if arg_match:
        return arg_match.groups()
    raise argparse.ArgumentTypeError("Argument does not match "
                                     "name=value format: {}".format(arg))


def parse_args(args_list=None):
    """Parse command line parameters.

    Returns:
        (object): Arguments(), immutable instance from ``.utils``.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--daemon",
                        help="Daemonise the ensembler", default=False,
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
    parser.add_argument("-l", "--shell",
                        help="Allows the user to specify the shell passed to "
                             "subprocess execs.",
                        default="/bin/bash", type=str)

    # FIXME: These should not be applied in multi-batch ensembles
    parser.add_argument("-k", "--skips",
                        help="Number of run entries to skip", default=0,
                        type=int)

    parser.add_argument("-i", "--indexes",
                        help="Specify which indexes to run",
                        type=parse_indexes)

    parser.add_argument("-ct", "--check-timeout", default=30, type=int)
    parser.add_argument("-st", "--submit-timeout", default=20, type=int)
    parser.add_argument("-rt", "--running-timeout", default=60, type=int)
    parser.add_argument("-et", "--error-timeout", default=120, type=int)

    parser.add_argument("-ms", "--max-stagger", default=1, type=int)

    parser.add_argument("-x", "--extra-vars", dest="extra", nargs="*",
                        default=[], type=parse_extra_vars)

    parser.add_argument("configuration")
    parser.add_argument("backend", default="slurm", choices=("slurm", "dummy"),
                        nargs="?")

    # Required to allow passing pre-set config to be 
    # passed as first positional argument
    if args_list is None:
        parsed_args = parser.parse_args()
    else:
        parsed_args = parser.parse_args(args_list)

    # Prefer retaining immutable Arguments()
    # by not using the instance as a namespace
    return Arguments(**vars(parsed_args))


def main(args=None):
    """CLI entry point.
    """
    if args is None:
        args = parse_args()

    if args.daemon:
        background_fork(True)

    setup_logging("{}".format(os.path.basename(args.configuration)),
                  verbose=args.verbose)

    logging.info("Model Ensemble Runner")

    config = EnsembleConfig(args.configuration)
    # TODO: get_batch_executor
    BatchExecutor(config,
                  args.backend,
                  dict(args.extra)).run()


def check():
    """CLI native sanity checking
    Contains pre-set sanity check configuration, combines them with
    the user's CLI arguments in a list (e.g. dummy/slurm), which is passed to main().
    
    Allow checking of successful installation.
    """
    # Get the user CLI args
    user_args = sys.argv[1:]

    # Directly pass sanity check yml + user args to
    # the argument parser as args_list
    args_list = ["examples/sanity-check.yml"] + user_args
    args = parse_args(args_list)

    main(args)
