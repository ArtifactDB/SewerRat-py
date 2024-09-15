import sewerrat
import os
import tempfile
import time


def test_list_registered_directories():
    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    _, url = sewerrat.start_sewerrat()

    sewerrat.register(mydir, ["metadata.json"], url=url)
    try:
        regged = sewerrat.list_registered_directories(url)
        assert len(regged) > 0

        found = False
        for x in regged:
            if x["path"] == mydir:
                found = True
                assert x["names"] == [ "metadata.json" ]
        assert found

        filtered = sewerrat.list_registered_directories(url, user=True)
        assert regged == filtered

        filtered = sewerrat.list_registered_directories(url, user=regged[0]["user"] + "_asdasdasd")
        assert len(filtered) == 0

    finally:
        sewerrat.deregister(mydir, url=url)

