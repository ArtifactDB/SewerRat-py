import sewerrat
import os
import tempfile
import time


def test_list_files():
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    _, url = sewerrat.start_sewerrat()

    sewerrat.register(mydir, ["metadata.json"], url=url)
    try:
        out = sewerrat.list_files(mydir, url=url)
        assert sorted(out) == [ "diet/metadata.json", "metadata.json" ]

        out = sewerrat.list_files(mydir + "/diet", url=url)
        assert sorted(out) == [ "metadata.json" ]

        out = sewerrat.list_files(mydir, url=url, force_remote=True)
        assert sorted(out) == [ "diet/metadata.json", "metadata.json" ]

    finally:
        sewerrat.deregister(mydir, url=url)
