from argparse import ArgumentParser
import os

import simple_logging_setup

from limepress.context import LimepressContext


def setup_parser(prog):
    parser = ArgumentParser(prog=prog)

    parser.add_argument(
        '-s',
        '--settings',
        nargs='+',
        default=[],
    )

    parser.add_argument(
        '-l',
        '--log-level',
        choices=['debug', 'info', 'warn', 'error', 'critical'],
        default='info',
    )

    parser.add_argument(
        '--loggers',
        type=str,
        nargs='+',
        default=[],
    )

    parser.add_argument(
        '-p',
        '--project-root',
        type=str,
        default=os.getcwd(),
    )

    return parser


def setup_logging(args):
    simple_logging_setup.setup(
        preset='cli',
        level=args.log_level,
        loggers=args.loggers,
        filter_logger_names=['limepress'],
    )


def setup_context(args):
    return LimepressContext(
        project_root=args.project_root,
        settings_paths=args.settings,
    )
