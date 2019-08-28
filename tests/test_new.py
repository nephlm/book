import os
import pytest

import book
import book.structure as struct


@pytest.fixture
def novel(tmp_path):
    novel = struct.Novel.create(tmp_path, convert=True)
    return novel


def test_new_novel(tmp_path):
    struct.Novel.create(tmp_path, convert=True)
    assert (tmp_path / "MANUSKRIPT").exists()
    assert (tmp_path / "outline").exists()
    assert (tmp_path / "outline").is_dir()


def test_new_folder(novel):
    folder_path = os.path.join(novel.path, "outline", "1-folder1")
    book.new_folder(novel.path, folder_path, convert=False)

    assert os.path.exists(folder_path)
    assert os.path.isdir(folder_path)


def test_new_scene(novel):
    scene_path = os.path.join(novel.path, "outline", "1-scene1.md")
    book.new_scene(novel.path, scene_path, convert=False)

    assert os.path.exists(scene_path)
    assert os.path.isfile(scene_path)
