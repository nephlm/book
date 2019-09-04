"""
File system utilities.  Differnetiated from structure as these functions are usually called before 
the novel object has been created.  Often used to decide what sort of structure object to be created
or to gather data needed to instantiate those object.
"""

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
            if is_path_a_novel(curr_path):
                return curr_path
        except FileNotFoundError:
            pass
        curr_path, _ = os.path.split(curr_path)
    return None


def is_path_a_novel(path):
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        return False
    # print(os.listdir(path))
    return struct.Novel.ANCHOR in os.listdir(path)


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
    """
    Extract the title from the path, peels off the order number.
    """
    filename = os.path.split(path)[1]
    try:
        return os.path.splitext(filename.split("-")[1])[0]
    except IndexError:
        return None
