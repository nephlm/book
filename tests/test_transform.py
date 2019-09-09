import argparse
import os

import book


def test_softcrlf_multiline_meta(novel):
    print(novel.path)
    scene_path = os.path.join(novel.outline.path, '0-test.md')
    book.new_scene(novel.path, scene_path, convert=False)
    scene = book.structure.Scene(scene_path)
    header = scene.header_dict
    header_test = 'some text\n  \n  The next line of text'
    header['test'] = header_test
    body = 'p1\np2\n'
    scene.rewrite(header=header, body=body)

    args = argparse.Namespace(softcrlf=True, hardcrlf=False, path=novel.path)
    book.show_transform(args)

    scene.reload_file()
    assert scene.header_dict['test'] == 'some text\n\nThe next line of text'
    # These leading three \n's shouldn't be here, not sure where they come from.
    assert scene.body == '\n\n\np1\n\np2'
