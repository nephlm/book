import logging
import os
import sys
import time

import prompter

import book.cli as cli
import book.session as sess
import book.structure as struct

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def arg_parser():
    # logger.info("arg_parser")
    parser = cli.get_parser()
    args = parser.parse_args()
    return args


def main():
    mapping = {
        cli.SESSION: show_session,
        cli.WORK: show_work,
        cli.RENAME: show_rename,
        cli.TRANSFORM: show_transform,
    }
    args = arg_parser()
    fx = mapping.get(args.command)
    if fx is None:
        show_stats(args)
    else:
        fx(args)


def show_stats(args):
    novel = struct.Novel(args.path)
    novel.reload_dir()
    for scene in novel.scenes(recursive=True):
        print(f"{scene.order:02d}, {scene.count:>5}, {scene.title}")

    print(f"count = {novel.count}")
    print(f"max pk = {novel.max_pk}")


def show_work(args):
    novel = struct.Novel(args.path)
    pre_changes = novel.auto_rename(dry_run=True)
    for change in pre_changes:
        if change[0] != change[1]:
            print("----" + change[0])
            print("++++" + change[1])
    if not args.dry_run:
        if prompter.yesno("Rename these files?"):
            novel.auto_rename(args.dry_run)
            print("Files renamed.")


def show_session(args):
    def run(session):
        cached = ""
        if not session.is_changed:
            cached = " (cached)"
        print(
            f" {session.count}/{session.goal} - Session; {session.start} start; {session.total_count} total; {cached}                ",
            end="\r",
        )

    novel = struct.Novel(args.path)
    session = sess.Session(novel, args.goal, args.start)
    while True:
        run(session)
        time.sleep(10)


def show_rename(args):
    novel = struct.Novel(args.path)
    pre_changes = novel.auto_rename(dry_run=True)
    for change in pre_changes:
        if change[0] != change[1]:
            print("----" + change[0])
            print("++++" + change[1])
    if not args.dry_run:
        if prompter.yesno("Rename these files?"):
            novel.auto_rename(args.dry_run)
            print("Files renamed.")


def show_transform(args):
    novel = struct.Novel(args.path)
    if args.softcrlf:
        print("Transforming novel to soft crlf format.")
        novel.transform_soft_crlf()
    if args.hardcrlf:
        print("Transforming novel to hard crlf format.")
        novel.transform_hard_crlf()


if __name__ == "__main__":
    main()
