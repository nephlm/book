import pytest

import book.structure as struct


@pytest.fixture
def novel(tmp_path):
    novel = struct.Novel.create(tmp_path, convert=True)
    return novel
