import logging
import os
import re
import string
import sys
import time

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)


class Novel(object):
    DEFAULT_FILENAME = "novel.md"
    CACHE_PERIOD = 10  # seconds

    def __init__(self, path):
        if "outline" not in path:
            path = os.path.join(path, "outline")
        self.path = path

        if os.path.isfile(path):
            self.folder_path, self.filename = os.path.split(path)
        else:
            self.folder_path = path
            self.filename = self.DEFAULT_FILENAME

        self._folders = None
        self._scenes = None
        self._other_files = None

        self._header_dict = None
        self._body = None

        self._cached_bytes = 0
        self._dir_read_time = 0
        self._file_read_time = 0

    def __repr__(self):
        return f"{self.__class__} {self.folder_path} {self.filename}"

    @property
    def file_path(self):
        return os.path.join(self.folder_path, self.filename)

    @property
    def header_dict(self):
        if self._header_dict is None or self.file_cache_expired:
            self.reload_file()
        return self._header_dict

    @property
    def body(self):
        if self._body is None or self.file_cache_expired:
            self.reload_file()
        return self._body

    @property
    def dir_cache_expired(self):
        return (time.time() - self._dir_read_time) > self.CACHE_PERIOD

    @property
    def file_cache_expired(self):
        return (time.time() - self._file_read_time) > self.CACHE_PERIOD

    @property
    def children(self):
        return sorted(self.folders() + self.scenes())

    @property
    def pk(self):
        try:
            return int(self.header_dict.get("ID", 0))
        except ValueError:
            return 0

    @property
    def title(self):
        return self.header_dict.get("title", self.filename)

    @property
    def safe_title(self):
        valid = string.ascii_letters + string.digits
        safe_name = ""
        for c in self.title:
            if c in valid:
                safe_name += c
            elif c in string.whitespace:
                safe_name += "_"
            else:
                safe_name += "-"
        return safe_name

    @property
    def count(self):
        count = len(self.body.split())
        # logger.debug(f"count={count}; {self.filename}")
        for folder in self.children:
            count += folder.count
        return count

    @property
    def byte_count(self):
        try:
            total = os.path.getsize(self.path)
        except FileNotFoundError:
            total = 0
        for child in self.children:
            total += child.byte_count
        self._cached_bytes = total
        return total

    @property
    def is_changed(self):
        cached_bytes = self._cached_bytes
        return cached_bytes != self.byte_count

    @property
    def max_pk(self):
        high = 0
        for child in self.children:
            high = max(high, child.max_pk)
        try:
            high = max(high, self.pk)
        except AttributeError:
            pass
        return high

    def folders(self):
        if self._folders is None or self.dir_cache_expired:
            self.reload_dir()
        return self._folders

    def scenes(self, recursive=False):
        if self._scenes is None or self.dir_cache_expired:
            self.reload_dir()
        if recursive:
            ret_list = []
            for child in self.children:
                if isinstance(child, Scene):
                    ret_list.append(child)
                else:
                    ret_list += child.scenes(recursive=True)
            return ret_list
        else:
            return self._scenes

    def other_files(self):
        if self._other_files is None or self.dir_cache_expired:
            self.reload_dir()
        return self._other_files

    def reload_dir(self):
        self._folders = []
        self._scenes = []
        self._other_files = []
        for file in os.listdir(self.path):
            if file == self.DEFAULT_FILENAME:
                self.reload_file()
            file_path = os.path.join(self.path, file)
            # logger.debug(file_path)
            if os.path.isfile(file_path):
                scene = Scene(file_path)
                if scene.is_scene:
                    self._scenes.append(scene)
                else:
                    self._other_files.append(file_path)
            else:
                self._folders.append(Folder(file_path))
        self._folders = sorted(self._folders)
        self._scenes.sort()
        self._dir_read_time = time.time()

    def reload_file(self, raise_errors=False):
        # logger.debug(f"filespec: {self.folder_path} || {self.filename}")
        try:
            with open(self.file_path) as fp:
                raw_content = fp.read().strip()
                # logger.debug(f"rc = {raw_content}")
                try:
                    header, body = raw_content.split("\n\n", 1)
                except ValueError:
                    header, body = raw_content, ""
                self._raw_header = header
                self._header_dict = self.extract_dict_from_file(header)
                self._body = body
                self._file_read_time = time.time()
        except FileNotFoundError:
            if raise_errors:
                raise
            self._raw_header = ""
            self._header_dict = {}
            self._body = ""

    @staticmethod
    def extract_dict_from_file(content):
        curr_key = None
        hdict = {}
        try:
            for line in content.split("\n"):
                # print(line)
                # print(line[0])
                if not line:
                    continue
                if line[0] != " ":
                    curr_key, val = line.split(":", 1)
                    curr_key = curr_key.strip()
                    hdict[curr_key] = val.strip()
                else:
                    val = line.strip()
                    hdict[curr_key] = hdict[curr_key] + val.strip()
        except ValueError:
            pass
            raise
        return hdict

    @property
    def order_digits(self):
        return len(str(len(self.folders()) + len(self.scenes())))

    def auto_rename(self, dry_run):
        digits = self.order_digits
        local_ops = []
        child_ops = []
        for child in self.folders():
            ops = child.auto_rename(dry_run)
            child_ops += ops

        for idx, child in enumerate(self.children):
            old_path = child.path
            ext = ""
            if isinstance(child, Scene):
                ext = ".md"
            new_filename = f"{idx:0{digits}}-{child.safe_title}{ext}"
            new_path = os.path.join(self.folder_path, new_filename)
            if old_path != new_path and os.path.exists(new_path):
                new_filename = f"{idx:0{digits}}-{child.safe_title}-{child.pk}{ext}"
                new_path = os.path.join(self.folder_path, new_filename)
            local_ops.append((old_path, new_path))

        if not dry_run:
            for op in local_ops:
                if op[0] != op[1]:
                    print(f"renaming {op[0]} --> {op[1]}")
                    os.rename(op[0], op[1])
        return local_ops + child_ops

    def rewrite(self, header=None, body=None):
        """
        Will rewrite the file from the values in of self._raw_header and self._body.
        """
        if header is None:
            header = self._raw_header
        if body is None:
            body = self._body
        if header or body:
            try:
                with open(self.file_path, "w") as fp:
                    fp.write("\n\n".join([header, body]))
            except IOError:
                logger.error(f"Attempt to rewrite file {self.file_path} failed!")
                raise

    def transform_hard_crlf(self):
        self._transform_sub_regex(r"\n+", "\n")
        for child in self.children:
            child.transform_hard_crlf()

    def transform_soft_crlf(self):
        self._transform_sub_regex(r"\n", "\n\n")
        for child in self.children:
            child.transform_soft_crlf()

    def _transform_sub_regex(self, pattern, replace):
        logger.debug(f"file_path: {self.file_path}")
        try:
            self.reload_file(raise_errors=True)
            body = re.sub(pattern, replace, self._body)
            if body != self._body:
                logger.debug("made a change")
                self.rewrite(body=body)
                self.reload_file
        except FileNotFoundError:
            # File doesn't exist
            logger.warn(
                f"Trying to transform file that does not exist: {self.file_path}"
            )


class Folder(Novel):
    DEFAULT_FILENAME = "folder.txt"

    def __init__(self, path, filename="folder.txt"):
        super().__init__(path)

    @property
    def order(self):
        try:
            filename = self.filename
            if self.filename == self.DEFAULT_FILENAME:
                filename = os.path.split(self.folder_path)[1]
            num = filename.split("-")[0]
            num = float(num)
            if num == int(num):
                num = int(num)
            return num
        except (IndexError, ValueError):
            return None

    def __eq__(self, other):
        return self.order == other.order

    def __ne__(self, other):
        return self.order != other.order

    def __lt__(self, other):
        return self.order < other.order

    def __le__(self, other):
        return self.order <= other.order

    def __gt__(self, other):
        return self.order > other.order

    def __te__(self, other):
        return self.order >= other.order


class Scene(Folder):
    DEFAULT_FILENAME = None

    def __init__(self, path):
        super().__init__(path)

    @property
    def is_scene(self):
        # logger.debug(os.path.splitext(self.filename))
        # logger.debug(os.path.isfile(self.path))
        # logger.debug(os.path.splitext(self.filename)[1] in (".txt", ".md"))
        # logger.debug(self.order is not None)

        if (
            os.path.isfile(self.path)
            and (os.path.splitext(self.filename)[1] in (".txt", ".md"))
            and (self.order is not None)
        ):
            # logger.debug("is scene")
            return True
        else:
            return False

    def folders(self):
        return []

    def scenes(self):
        return []

    def other_files(self):
        return []

