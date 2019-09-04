import os.path

import book.structure as struct


def test_level(novel):
    path = novel.outline.path
    chapter1 = struct.Folder.create(os.path.join(path, "1-chapter1"))
    assert chapter1.level == 1
    chapter2 = struct.Folder.create(os.path.join(path, "2-chapter2"))
    assert chapter2.level == 1
    chapter2_1 = struct.Folder.create(os.path.join(path, "2-chapter2", "1-chapter3"))
    assert chapter2_1.level == 2
    scene2_1 = struct.Scene.create(os.path.join(path, "2-chapter2", "1-scene1"))
    assert scene2_1.level == 2
    scene2_1 = struct.Scene.create(
        os.path.join(path, "2-chapter2", "1-chapter3", "1-scene1")
    )
    assert scene2_1.level == 3


def test_metadata_level(novel):
    path = novel.outline.path
    chapter1 = struct.Folder.create(os.path.join(path, "1-chapter1"))
    chapter1.header_dict["level"] = 3
    chapter1.rewrite()

    new_chapt1 = struct.Folder(os.path.join(path, "1-chapter1"))
    assert new_chapt1.level == 3
