#! /usr/bin/env python3

import argparse
import os.path
import time
import zipfile


class ZipFileInterface(zipfile.ZipFile):
    """
    Interface that matches zipfile for projects saved unzipped.
    """
    def __init__(self, root):
        self.root = root
        if self.root[-1] != '/':
            self.root += '/'

    def open(self, zipinfo):
        return open(zipinfo.full_path, 'rb')

    def getinfo(self, path):
        return ZipInfoInterface(self.root, path)

    def infolist(self):
        import glob
        files = []
        for root, folders, filenames in os.walk(self.root):
            in_zip_part = root.replace(self.root, '')
            for f in filenames:
                files.append(ZipInfoInterface(self.root, os.path.join(in_zip_part, f)))
        return files

    def close(self):
        # Nothing to do.
        pass

class ZipInfoInterface():
    def __init__(self, root, path):
        self.root = root
        self.path = path
        self.full_path = os.path.join(root, path)

    def read(self):
        with open(self.full_path) as fp:
            return fp.read()
    
    @property
    def filename(self):
        return self.path

    def __repr__(self):
        return f'ZipInfo({self.root} / {self.path})'

class Folder(object):
    def __init__(self, zf, zipinfo):
        self.zf = zf
        self.zipinfo = zipinfo
        self.path = zipinfo.filename
        self._parent_compile = None
        self._parent = None
        self._children = None

        self.content = zf.open(zipinfo).read().decode('utf8').strip()
        self.base_path, self.filename = os.path.split(self.path)
        if self.filename == 'folder.txt':
            self.header_dict = extract_dict_from_file(self.content)
        else:
            self.header_dict = {}

    @property
    def is_folder(self):
        print(self.filename)
        return self.filename == 'folder.txt'

    @property
    def pk(self):
        pk = self.header_dict.get('ID')
        if pk:
            try:
                pk = int(pk)
            except ValueError:
                pk = None
        return pk

    @property
    def order_num(self):
        try:
            base_path, filename = os.path.split(self.path)
            if filename == 'folder.txt':
                filename = os.path.split(base_path)[1]
            num = filename.split('-')[0]
            num = float(num)
            if num == int(num):
                num = int(num)
            return num
        except (IndexError, ValueError):
            return None

    @property
    def max_order_num(self):
        max_num = 0
        if not self.is_folder:
            return self.order_num
        else:
            for child in self.get_children():
                order = child.order_num
                if order > max_num:
                    max_num = order
            return max_num


    @property
    def total_order(self):
        

        parent_path = self.get_parent_path()
        #if 'folder.txt' in parent_path:

        #print (self.path, parent_path)
        if parent_path == self.path:
            if self.total_order is not None:
                return int(self.total_order)
            else:
                return 0
        else:
            if parent_path:
                try:
                    if not self._parent:
                        self._parent = Folder(self.zf, self.zf.getinfo(parent_path))
                    #print(parent.base_path)
                    parent_order = self._parent.total_order
                except FileNotFoundError:
                    parent_order = 0
                    
            if self.order_num is not None:
                return (parent_order * 1000) + self.order_num
            else:
                return (parent_order * 1000)
            
    def get_children(self):
        if not self.is_folder:
            return []
        elif self._children is not None:
            return self._children
        else:
            self._children = []
            all_items = self.zf.infolist()
            for item in [x for x in all_items if self.base_path in x.filename]:
                if 'folder.txt' in item.filename:
                    self._children.append(Folder(self.zf, item))
                else:
                    self._children.append(Scene(self.zf, item))
            return self._children

    def get_parent_path(self):
        parent_base_path = os.path.split(self.base_path)[0]
        #print(self.base_path, parent_base_path)
        return os.path.join(parent_base_path, 'folder.txt')

    def parent_compile(self):
        if self._parent_compile is not None:
            return self._parent_compile
        parent_path = self.get_parent_path()
        if parent_path == 'outline/folder.txt':
            return True
        if not self._parent:
            self._parent = Folder(self.zf, self.zf.getinfo(parent_path))
        self._parent_compile = self._parent.is_compiled()
        # print(f'PC: {parent_path}  ||  {parent.is_compiled()}')
        return self._parent_compile

    def is_compiled(self):
        # print(self.path)
        if self.header_dict.get('compile') == '2' and self.parent_compile():
            return True
        # print(f'{self.path} | {self.header_dict["compile"]}')
        return False


    def count(self, recursive=False):
        if recursive:
            raise NotImplementedError('recursive count isn\'t implemented yet.')
        return 0

    def __eq__(self, other):
        return self.total_order == other.total_order
    def __ne__(self, other):
        return self.total_order != other.total_order
    def __lt__(self, other):
        return self.total_order < other.total_order
    def __le__(self, other):
        return self.total_order <= other.total_order
    def __gt__(self, other):
        return self.total_order > other.total_order
    def __te__(self, other):
        return self.total_order >= other.total_order
    

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
        try:
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
        except ValueError:
            pass
        return hdict


class Session(object):
    def __init__(self, path, goal=1000, start=None):
        self.path = path
        self.goal = goal
        self.start = start
        self.filesize = None
        self.cache_total_count = None
        self.filestore = FileStore(self.path)

        if start is None:
            self.start = self.total_count()

    def is_changed(self):
        return self.filestore.filesize() != self.filesize


    def total_count(self):
        if not self.is_changed():
            return self.cache_total_count
        
        zf = self.filestore.zipfile_interface()
        total = 0
        for scene in self.filestore.get_files():
            if scene.is_compiled:
                total += scene.count()
        self.cache_total_count = total
        return total


    def count(self):
        return self.total_count() - self.start

class FileStore(object):
    def __init__(self, path):
        self.path = path
        self.is_zip = True
        if os.path.isdir(path):
            self.is_zip = False

    def filesize(self):        
        if self.is_zip:
            return os.path.getsize(self.path)
        else: 
            total = 0
            for root, dirs, files in os.walk(self.path):
                if 'outline' not in root:
                    continue 
                for f in files:
                    total += os.path.getsize(os.path.join(root, f))
            return total

    def zipfile_interface(self):
        if self.is_zip:
            return zipfile.ZipFile(self.path)
        else:
            return ZipFileInterface(self.path)

    def get_files(self, include_scenes=True, include_folders=False):
        zf = self.zipfile_interface()
        folder = None
        files = []
        for zipinfo in zf.infolist():
            if (zipinfo.filename.startswith('outline') and
                    not zipinfo.filename.endswith('folder.txt')):
                base_path = os.path.split(zipinfo.filename)[0]
                if include_folders:
                    if folder is None or folder.base_path != base_path:
                        folder = Folder(zf, zf.getinfo(os.path.join(base_path, 'folder.txt')))
                        files.append(folder)
                if include_scenes:
                    scene = Scene(zf, zipinfo)
                    files.append(scene)
        # zf.close()
        return files


def run(session):
    cached = ''
    try:
        if not session.is_changed():
            cached = ' (cached)'
        print(f' {session.count()}/{session.goal} - Session; {session.start} start; {session.total_count()} total; {cached}                ', end='\r')
        session.filesize = os.path.getsize(session.path)
    except zipfile.BadZipFile:
        print('BadZipFile    ')


def run_loop(args):
    session = Session(args.path, args.goal, args.start)
    while True:
        run(session)
        time.sleep(10)


def show_stats(args):
    fs = FileStore(args.path)
    total = fs.filesize()
    scenes = sorted(fs.get_files(include_folders=True))
    words = 0
    maxid = -1
    for scene in scenes:
        print((scene.path, scene.pk, scene.order_num, scene.total_order, scene.count()))
        words += scene.count()
        if scene.pk > maxid:
            maxid = scene.pk
    print(f'Total Bytes = {total}')
    print(f'Max ID = {maxid}')
    print(f'Total Words = {words}')


def run_test(args):
    fs = FileStore(args.path)
    for scene in fs.get_files(include_scenes=False, include_folders=True):
        print(scene.filename, scene.max_order_num)

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
    parser.add_argument('--stats', action='store_true',
                        default=False,
                        help='Show some stats.')
    parser.add_argument('--test', action='store_true',
                        default=False,
                        help='Run the test function')

    args = parser.parse_args()
    if args.test:
        run_test(args)
    elif args.stats:
        show_stats(args)
    else:
        run_loop(args)
