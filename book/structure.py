"""
The lion's share of the project.

Manages the novel structure and the outline hierarchy.  Many of these functions are recursive walking 
through folders and files.

This hierarchy is based on the manuskript .msk format (but not set to save as a single file), but there are
some differences.  The README.md should have relevant information. 
"""

import logging
import os
import re
import string
import sys
import time

from typing import Optional

import book.metadata as mdata
import book.fs_utils as fs_utils

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logger = logging.getLogger(__name__)


class Novel(object):
    """
    Top level novel structure.  This is the path that is passed into most of the commands.
    """

    OUTLINE_DIR = "outline"
    ANCHOR = "MANUSKRIPT"

    def __init__(self, path):
        self.path = path
        self._outline = None

    @property
    def outline_path(self):
        return os.path.join(self.path, self.OUTLINE_DIR)

    @property
    def outline(self):
        if self._outline is None:
            self._outline = Outline(self.outline_path)
        return self._outline

    @classmethod
    def is_path_a_novel(cls, path):
        if not os.path.exists(path):
            return False
        if not os.path.isdir(path):
            return False
        # print(os.listdir(path))
        return cls.ANCHOR in os.listdir(path)

    @classmethod
    def create(cls, path, convert=False):
        try:
            os.makedirs(path)
        except FileExistsError:
            if not convert:
                raise

        title = os.path.split(path)[1]
        with open(os.path.join(path, cls.ANCHOR), "w") as fp:
            fp.write("1\n")
        novel = cls(path)
        # novel.outline.create()
        Outline.create(novel.outline_path, convert, title)
        return novel

    def compile(self) -> str:
        single_string = self.compile_frontmatter()
        single_string += self.outline.compile_string()
        single_string += self.compile_backmatter()
        single_string = self.clean_compile(single_string)
        return single_string

    def compile_frontmatter(self) -> str:
        # return f"# {self.outline.title}\n\n"
        return ''

    def compile_backmatter(self) -> str:
        return ""

    def clean_compile(self, single_string):
        while '\n\n\n' in single_string:
            single_string = single_string.replace('\n\n\n', '\n\n')
        return single_string


class Outline(object):
    """
    The outline directory.  It contains folders and scenes. The underlying folders can further contain
    folders and scenes. 

    Folder and scenes inherit from this class and many of the methods are self aware and operate properly 
    in any of those cases. 
    """

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

    @classmethod
    def get_file_path(cls, path):
        return os.path.join(path, cls.DEFAULT_FILENAME)

    @classmethod
    def create_folders(cls, path, convert):
        """
        Create all the required directories for a Folder path to exist. 
        """
        try:
            os.makedirs(path)
        except FileExistsError:
            if not convert:
                raise

    @classmethod
    def create(cls, path, convert=False, title=None, ID=None):
        cls.create_folders(path, convert)

        metadata = mdata.DEFAULT_METADATA.copy()
        if title is not None:
            metadata[mdata.TITLE] = title
        else:
            metadata[mdata.TITLE] = fs_utils.title_from_path(path)

        if ID is not None:
            metadata[mdata.ID] = ID
        elif cls is Outline:
            metadata[mdata.ID] = 1

        file_path = cls.get_file_path(path)
        if convert:
            try:
                with open(file_path, "r") as fp:
                    content = fp.read()
            except FileNotFoundError:
                content = ""
        else:
            content = ""

        with open(file_path, "w") as fp:
            fp.write(mdata.dict_to_metadata_string(metadata))
            fp.write(f"\n\n{content}")
        obj = cls(path)
        return obj

    @property
    def structure_metadata(self) -> str:
        """
        The semantic position of this object in the novel (novel, chapter, scene)

        It is possible for subclasses to return None and use the default. 
        """
        return mdata.NOVEL

    @property
    def is_chapter(self) -> bool:
        semantic = self.header_dict.get(mdata.STRUCTURE, mdata.SCENE)
        return semantic == mdata.CHAPTER

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
        """
        not idempotent
        """
        cached_bytes = self._cached_bytes
        return cached_bytes != self.byte_count

    @property
    def max_pk(self):
        try:
            high = int(self.header_dict.get(mdata.ID, 0))
        except TypeError:
            print(f"ID in {self.path} is not an int")
            high = 0
        # print(f"local high: {high}")
        for child in self.children:
            # print(f"{child.filename}: {child.max_pk}")
            high = max(high, child.max_pk)
        try:
            high = max(high, self.pk)
        except AttributeError:
            pass
        return high

    @property
    def level(self) -> int:
        """
        Return the number of levels deep this structure is from outline
        .../outline/Novel.md -> 0
        .../outline/1-folder/folder.txt -> 1
        .../outline/1-folder/scene.md -> 2
        """
        if mdata.LEVEL in self.header_dict:
            try:
                return int(self.header_dict[mdata.LEVEL])
            except ValueError:
                pass

        novel_path = fs_utils.find_novel_in_path(self.path)
        remainder = self.path.replace(novel_path, "")
        level = 0
        while "outline" in remainder:
            # print(remainder)
            remainder, _ = os.path.split(remainder)
            level += 1

        return level - 1

    def folders(self, recursive=False):
        if self._folders is None or self.dir_cache_expired:
            self.reload_dir()
        if recursive:
            ret_list = []
            for folder in self._folders:
                ret_list.append(folder)
                ret_list += folder.folders(recursive=True)
            return ret_list
        else:
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
                # directory
                folder = Folder(file_path)
                if folder.order is not None:
                    self._folders.append(folder)
                else:
                    self._other_files.append(folder)

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
        Will rewrite the file from the values in of self.header and self._body.
        """
        if header is None:
            header = self.header_dict
        if body is None:
            body = self._body
        if header or body:
            try:
                with open(self.file_path, "w") as fp:
                    fp.write("\n\n".join([mdata.dict_to_metadata_string(header), body]))
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

    def compile_string(self) -> str:
        single_string = self.compile_frontmatter()
        single_string += self.body
        for child in self.children:
            single_string += child.compile_string()
        single_string += self.compile_backmatter()
        return single_string

    def compile_frontmatter(self) -> str:
        frontmatter = ""
        if self.is_chapter:
            frontmatter += f"\n\n# {self.title}\n\n"
        return frontmatter

    def compile_backmatter(self) -> str:
        return ""


class Folder(Outline):
    """
    A folder underneath the outline path or a parent folder. 
    """

    DEFAULT_FILENAME = "folder.txt"

    def __init__(self, path, filename="folder.txt"):
        super().__init__(path)

    @property
    def structure_metadata(self) -> str:
        """
        The semantic position of this object in the novel (novel, chapter, scene)
        
        It is possible for subclasses to return None and use the default. 

        Although in many cases a folder should be considered a chapter, not all folders are chapters.
        The default will be to create the folder as chapter.

        This should return 'chapter' if that turns out to be the wrong choice change this to None so the 
        default of scene is used. 
        """
        return mdata.CHAPTER

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

    def __ge__(self, other):
        return self.order >= other.order


class Scene(Folder):
    """
    a scene .md file under a folder. It maintains the interface of Folder so the walking the hierarchy 
    down to files doesn't cause any issues.
    """

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

    @classmethod
    def get_file_path(cls, path):
        return path

    @classmethod
    def create_folders(cls, path, convert):
        """
        Overrides parent's `create_folders` since self.path is a file and not a folder. 
        """
        parent_dir = os.path.split(path)[0]
        if not os.path.exists(parent_dir):
            raise FileNotFoundError(
                f"{parent_dir} does not exist.  Is the path correct?"
            )
        if os.path.exists(path) and not convert:
            raise FileExistsError(
                f"{path} already exists, did you want to --convert it?"
            )

    @property
    def structure_metadata(self) -> Optional[str]:
        """
        The semantic position of this object in the novel (novel, chapter, scene)
        
        Returning None will use the implied default of scene. 
        """
        return None
