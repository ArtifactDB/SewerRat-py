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

    sewerrat.start_sewerrat()

    try:
        sewerrat.register(mydir, ["metadata.json"])

        res = sewerrat.query("aaron")
        assert len(res) == 1

        res = sewerrat.query("lun%") 
        assert len(res) == 2

        res = sewerrat.query("lun% AND aaron")
        assert len(res) == 1

        res = sewerrat.query("meal:lun%")
        assert len(res) == 1

        res = sewerrat.query(path="diet/") # has 'diet/' in the path
        assert len(res) == 1

        res = sewerrat.query(after=time.time() - 60)
        assert len(res) == 2

        # Successfully deregistered:
        sewerrat.deregister(mydir)

        res = sewerrat.query("aaron")
        assert len(res) == 0

    finally:
        # Okay, stop the service:
        sewerrat.stop_sewerrat()
