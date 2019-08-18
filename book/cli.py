import argparse
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

SESSION = "session"
STATS = "stats"
WORK = "work"
RENAME = "rename"
TRANSFORM = "transform"


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
        "--dry-run",
        "-n",
        default=False,
        action="store_true",
        help="Don't actually rename anything",
    )
    return parser


def get_transform_parser(sub_parsers):
    parser = sub_parsers.add_parser(
        TRANSFORM, help="Perform transformations on the text."
    )
    parser.add_argument(
        "--softcrlf",
        default=False,
        action="store_true",
        help="Create whitespace between paragraphs for easier editing.",
    )
    parser.add_argument(
        "--hardcrlf",
        default=False,
        action="store_true",
        help="Remove whitespace between paragraphs.",
    )
    return parser


def get_rename_parser(sub_parsers):
    parser = sub_parsers.add_parser(RENAME, help="Auto rename files based on metadata")
    parser.add_argument(
        "--dry-run",
        "-n",
        default=False,
        action="store_true",
        help="Don't actually rename anything",
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
    get_rename_parser(sub_parsers)
    get_work_parser(sub_parsers)
    get_transform_parser(sub_parsers)

    return parser
