import os.path

import book.structure as struct


def find_novel_in_path(path):
    """
    Walk up the path looking for novel.md or the root.
    Return the directory containing novel.md or None if no parent directory
    contains novel.md
    """
    curr_path = path
    while curr_path and curr_path != "/":
        # print(curr_path)
        try:
            if struct.Novel.is_path_a_novel(curr_path):
                return curr_path
        except FileNotFoundError:
            pass
        curr_path, _ = os.path.split(curr_path)
    return None


def has_order_digit(path):
    """
    return True if the leaf folder starts with a number
    """
    filename = os.path.split(path)[1]
    num_string = filename.split("-")[0]
    try:
        float(num_string)
        return True
    except ValueError:
        return False


def title_from_path(path):
    filename = os.path.split(path)[1]
    try:
        return filename.split("-")[1]
    except IndexError:
        return None
