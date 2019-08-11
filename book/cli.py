import argparse
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

SESSION = "session"
STATS = "stats"
WORK = "work"


def get_session_parser(sub_parsers):
    parser = sub_parsers.add_parser(SESSION, help="Track session goals")
    parser.add_argument(
        "--goal", metavar="GOAL", type=int, default=1000, help="Word count target."
    )
    parser.add_argument(
        "--start",
        metavar="START_COUNT",
        type=int,
        default=None,
        help="Set the session start value.",
    )
    return parser


def get_stats_parser(sub_parsers):
    parser = sub_parsers.add_parser(STATS, help="Scene stats sheet")
    return parser


def get_work_parser(sub_parsers):
    parser = sub_parsers.add_parser(
        WORK, help="Whatever was leftover from last dev sprint"
    )
    parser.add_argument(
        "--goal", metavar="GOAL", type=int, default=1000, help="Word count target."
    )
    parser.add_argument(
        "--start",
        metavar="START_COUNT",
        type=int,
        default=None,
        help="Set the session start value.",
    )
    return parser


def get_parser():
    # logger.info("get_parser-1")
    parser = argparse.ArgumentParser(description="Book Management.")
    
    sub_parsers = parser.add_subparsers(dest="command", help="Subcommand to run")
    parser.add_argument(
        "path", metavar="PATH", type=str, help="Path to book directory."
    )

    get_session_parser(sub_parsers)
    get_stats_parser(sub_parsers)
    get_work_parser(sub_parsers)

    return parser
