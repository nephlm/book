import logging
import os
import sys
import time
import zipfile

import book.cli as cli
import book.file_proc as FP
import book.structure as struct

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)


def arg_parser():
    logger.info("arg_parser")
    parser = cli.get_parser()
    args = parser.parse_args()
    return args


def main():
    mapping = {cli.SESSION: show_session, cli.WORK: show_work}
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
    novel.reload_dir()
    for scene in novel.scenes(recursive=True):
        print(f"{scene.order:02d}, {scene.count:>5}, {scene.title}")

    print(f"count = {novel.count}")
    print(f"max pk = {novel.max_pk}")



def show_session(args):
    def run(session):
        cached = ""
        try:
            if not session.is_changed():
                cached = " (cached)"
            print(
                f" {session.count()}/{session.goal} - Session; {session.start} start; {session.total_count()} total; {cached}                ",
                end="\r",
            )
            session.filesize = os.path.getsize(session.path)
        except zipfile.BadZipFile:
            print("BadZipFile    ")

    session = FP.Session(args.path, args.goal, args.start)
    while True:
        run(session)
        time.sleep(10)



if __name__ == "__main__":
    main()
