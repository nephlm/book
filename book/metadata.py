"""
Utilities to deal with the meta data for a scene/folder.
"""

TITLE = "title"
ID = "ID"
TYPE = "type"
COMPILE = "compile"

DEFAULT_METADATA = {TITLE: "title", ID: 0, TYPE: "md", COMPILE: 2}


def format_meta_data(name, value, tab_length=10):
    """
    Formats a single meta data item.
    Taken directly from manuskript originally.
    """
    # Multiline formatting
    if len(value.split("\n")) > 1:
        lines = value.split("\n")
        tab = " " * (tab_length + 1)
        value = "\n".join([tab + l for l in lines])[tab_length + 1 :]

    # Avoid empty description (don't know how much MMD loves that)
    if name == "":
        name = "None"

    # Escapes ":" in name
    name = name.replace(":", "_.._")

    spaces = " " * (tab_length - len(name))
    return f"{name}:{spaces}{value}\n"


def dict_to_metadata_string(dict, tab_length=15):
    """
    converts a dict to .mmd metadata string format.
    """
    st = ""
    for key, val in dict.items():
        if val is not None and val != "":
            st += format_meta_data(key, str(val), tab_length)
    return st
