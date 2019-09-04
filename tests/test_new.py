import os
import pytest

import book
import book.structure as struct


# @pytest.fixture
# def novel(tmp_path):
#     novel = struct.Novel.create(tmp_path, convert=True)
#     return novel


def test_new_novel(tmp_path):
    struct.Novel.create(tmp_path, convert=True)
    assert (tmp_path / "MANUSKRIPT").exists()
    assert (tmp_path / "outline").exists()
    assert (tmp_path / "outline").is_dir()

    novel = struct.Novel(tmp_path)
    outline = novel.outline
    assert outline.filename == "novel.md"
    assert outline.header_dict["title"].startswith("test_new_novel")
    assert outline.header_dict["type"] == "md"
    assert outline.header_dict["ID"]
    assert outline.header_dict["compile"] == "2"


def test_new_folder(novel):
    path = novel.outline.path
    folder_path = os.path.join(path, "1-folder1")
    book.new_folder(novel.path, folder_path, convert=False)

    assert os.path.exists(folder_path)
    assert os.path.isdir(folder_path)

    folder = struct.Folder(os.path.join(path, "1-folder1"))
    assert folder.filename == "folder.txt"
    assert folder.header_dict["title"] == "folder1"
    assert folder.header_dict["type"] == "md"
    assert folder.header_dict["ID"]
    assert folder.header_dict["compile"] == "2"


def test_new_scene(novel):
    path = novel.outline.path
    scene_path = os.path.join(path, "1-scene1.md")
    book.new_scene(novel.path, scene_path, convert=False)

    assert os.path.exists(scene_path)
    assert os.path.isfile(scene_path)

    scene = struct.Scene(os.path.join(path, "1-scene1.md"))
    assert scene.header_dict["title"] == "scene1"
    assert scene.header_dict["type"] == "md"
    assert scene.header_dict["ID"]
    assert scene.header_dict["compile"] == "2"

