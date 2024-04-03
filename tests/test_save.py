import biocframe
import sewerrat
import tempfile
import os


def test_save():
    dir = tempfile.mkdtemp()

    test = biocframe.BiocFrame({ "A": [1,2,3,4,5], "B": ["x", "y", "z", "aa", "bb"] })
    sewerrat.quick_save(test, { "title": "data frame", "description": "I am a data frame" }, os.path.join(dir, "foobar"))

    assert os.path.exists(os.path.join(dir, "foobar", "_metadata.json"))
    assert os.path.exists(os.path.join(dir, "foobar", "OBJECT"))

    retest, remeta = sewerrat.quick_read(os.path.join(dir, "foobar"))
    assert isinstance(retest, biocframe.BiocFrame)
    assert retest.get_column_names().as_list() == [ "A", "B" ]
    assert remeta["title"] == "data frame"
