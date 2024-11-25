import sewerrat
import os
import tempfile
import time
import pytest


def test_query_truncation(capfd):
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    _, url = sewerrat.start_sewerrat()
    sewerrat.register(mydir, ["metadata.json"], url=url)

    res = sewerrat.query(url, "lun", number=0)
    out, err = capfd.readouterr()
    assert "truncated" in out
    assert len(res) == 0

    with pytest.warns(UserWarning, match="truncated"):
        res = sewerrat.query(url, "lun", number=0, on_truncation="warning")
    assert len(res) == 0

    res = sewerrat.query(url, "lun", number=0, on_truncation="none")
    assert len(res) == 0
