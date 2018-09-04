#! /usr/bin/env python3

import argparse
import os.path
import time
import zipfile


class Folder(object):
    def __init__(self, zf, zipinfo):
        self.zf = zf
        self.zipinfo = zipinfo
        self.path = zipinfo.filename
        self._parent_compile = None

        self.content = zf.open(zipinfo).read().decode('utf8').strip()
        base_path, filename = os.path.split(self.path)
        self.base_path = base_path
        if filename == 'folder.txt':
            self.header_dict = extract_dict_from_file(self.content)
        else:
            self.header_dict = {}

    def get_parent_path(self):
        parent_base_path = os.path.split(self.base_path)[0]
        return os.path.join(parent_base_path, 'folder.txt')

    def parent_compile(self):
        if self._parent_compile is not None:
            return self._parent_compile
        parent_path = self.get_parent_path()
        if parent_path == 'outline/folder.txt':
            return True
        parent = Folder(self.zf, self.zf.getinfo(parent_path))
        self._parent_compile = parent.is_compiled()
        # print(f'PC: {parent_path}  ||  {parent.is_compiled()}')
        return self._parent_compile

    def is_compiled(self):
        # print(self.path)
        if self.header_dict['compile'] == '2' and self.parent_compile():
            return True
        # print(f'{self.path} | {self.header_dict["compile"]}')
        return False


class Scene(Folder):
    def __init__(self, zf, zipinfo):
        super().__init__(zf, zipinfo)
        try:
            self.header, self.body = self.content.split('\n\n', 1)
        except ValueError:
            self.header, self.body = self.content, ''
        self.header_dict = extract_dict_from_file(self.header)

    def count(self):
        return len(self.body.split())

    def get_parent_path(self):
        return os.path.join(self.base_path, 'folder.txt')


def extract_dict_from_file(content):
        curr_key = None
        hdict = {}
        for line in content.split('\n'):
            # print(line)
            # print(line[0])
            if not line:
                continue 
            if line[0] != ' ':
                curr_key, val = line.split(':', 1)
                curr_key = curr_key.strip()
                hdict[curr_key] = val.strip()
            else:
                val = line.strip()
                hdict[curr_key] = hdict[curr_key] + val.strip()
        return hdict


class Session(object):
    def __init__(self, path, goal=1000, start=None):
        self.path = path
        self.goal = goal
        self.start = start


        if start is None:
            self.start = self.total_count()

    def total_count(self):
        zf = zipfile.ZipFile(self.path)
        folder = None
        total = 0
        for zipinfo in zf.infolist():
            if (zipinfo.filename.startswith('outline') and 
                    not zipinfo.filename.endswith('folder.txt')):
                base_path = os.path.split(zipinfo.filename)[0]
                if folder is None or folder.base_path != base_path:
                    folder = Folder(zf, zf.getinfo(os.path.join(base_path, 'folder.txt')))
                scene = Scene(zf, zipinfo)
                if scene.is_compiled():
                    total += scene.count()
        zf.close()
        return total


    def count(self):
        return self.total_count() - self.start

def run(session):
    try:
        print(f' {session.count()}/{session.goal} - Session; {session.start} start; {session.total_count()} total                ', end='\r')
    except zipfile.BadZipFile:
        print('BadZipFile    ')


def run_loop(args):
    session = Session(args.path, args.goal, args.start)
    while True:
        run(session)
        time.sleep(1)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Session word count.')
    parser.add_argument('path', metavar='PATH', type=str, 
                        help='Path to .msk file.')
    parser.add_argument('--goal', metavar='GOAL', type=int, 
                        default=1000,
                        help='Word count target.')
    parser.add_argument('--start', metavar='START_COUNT', type=int, 
                        default=None,
                        help='Set the session start value.')

    args = parser.parse_args()    
    run_loop(args)