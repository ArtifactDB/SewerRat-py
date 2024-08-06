import sewerrat
import os
import tempfile
import time


def test_basic():
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    _, url = sewerrat.start_sewerrat()

    try:
        sewerrat.register(mydir, ["metadata.json"], url=url)

        res = sewerrat.query(url, "aaron")
        assert len(res) == 1

        res = sewerrat.query(url, "lun%")
        assert len(res) == 2

        res = sewerrat.query(url, "lun% AND aaron")
        assert len(res) == 1

        res = sewerrat.query(url, "meal:lun%")
        assert len(res) == 1

        res = sewerrat.query(url, path="diet/") # has 'diet/' in the path
        assert len(res) == 1

        res = sewerrat.query(url, after=time.time() - 60) 
        assert len(res) == 2

        # Successfully deregistered:
        sewerrat.deregister(mydir, url=url)

        res = sewerrat.query(url, "aaron")
        assert len(res) == 0

        # We can also register a string.
        sewerrat.register(mydir, "metadata.json", url=url)

        res = sewerrat.query(url, "aaron")
        assert len(res) == 1

    finally:
        # Okay, stop the service:
        sewerrat.stop_sewerrat()
