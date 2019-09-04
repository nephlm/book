import book.metadata as mdata


def test_dict_to_metadata_string():
    mdata_dict = {
        mdata.TITLE: "title",
        mdata.ID: 0,
        mdata.TYPE: "md",
        mdata.COMPILE: 2,
        mdata.LEVEL: 5,
    }
    mdata_str = mdata.dict_to_metadata_string(mdata_dict)
    answer = "title:          title\nID:             0\ntype:           md\ncompile:        2\nlevel:          5\n"
    print(mdata_str)
    assert mdata_str == answer
