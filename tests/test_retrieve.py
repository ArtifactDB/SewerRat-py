import sewerrat
from sewerrat.retrieve_directory import _local_root
import pytest
import os
import tempfile
import json
import time


@pytest.fixture(scope="module")
def setup():
    _, url = sewerrat.start_sewerrat()

    mydir = tempfile.mkdtemp()
    with open(os.path.join(mydir, "metadata.json"), "w") as handle:
        handle.write('{ "first": "Aaron", "last": "Lun" }')

    os.mkdir(os.path.join(mydir, "diet"))
    with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
        handle.write('{ "meal": "lunch", "ingredients": "water" }')

    sewerrat.register(mydir, ["metadata.json"], url=url)
    return mydir


def test_retrieve_file(setup):
    mydir = setup
    _, url = sewerrat.start_sewerrat()

    p = sewerrat.retrieve_file(mydir + "/metadata.json", url=url)
    with open(p, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # Caching of remotes works as expected.
    cache = tempfile.mkdtemp()
    p = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p.startswith(cache)
    with open(p, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # Subsequent requests are no-ops.
    with open(p, "w") as f:
        f.write('{ "first": "Erika" }')
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Erika"

    # Overwritten successfully:
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True, overwrite=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    # We also get an update if the cached file is too old.
    with open(p, "w") as f:
        f.write('{ "first": "Erika" }')
    os.utime(p, (time.time(), time.time() - 4000))
    p2 = sewerrat.retrieve_file(mydir + "/metadata.json", url=url, cache=cache, force_remote=True)
    assert p == p2 
    with open(p2, "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"


def test_retrieve_metadata(setup):
    mydir = setup
    _, url = sewerrat.start_sewerrat()

    fpath = mydir + "/diet/metadata.json"
    meta = sewerrat.retrieve_metadata(fpath, url=url)
    assert os.path.normpath(fpath) == os.path.normpath(meta["path"])
    assert meta["metadata"]["meal"] == "lunch"


def test_retrieve_directory(setup):
    mydir = setup
    _, url = sewerrat.start_sewerrat()

    dir = sewerrat.retrieve_directory(mydir, url=url)
    with open(os.path.join(dir, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["first"] == "Aaron"

    subpath = os.path.join(mydir, "diet")
    cache = tempfile.mkdtemp()
    rdir = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir.startswith(cache)
    with open(os.path.join(rdir, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Subsequent requests are no-ops.
    with open(os.path.join(rdir, "metadata.json"), "w") as f:
        f.write('{ "meal": "dinner" }')
    rdir2 = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "dinner"

    # Unless we force an overwrite.
    rdir2 == sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True, overwrite=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Or the cached file AND the success file are both too old, in which case they get updated.
    with open(os.path.join(rdir, "metadata.json"), "w") as f:
        f.write('{ "meal": "dinner" }')
    os.utime(os.path.join(rdir, "metadata.json"), (time.time(), time.time() - 4000))
    os.utime(os.path.join(_local_root(cache, url), "SUCCESS" + subpath, "....OK"), (time.time(), time.time() - 4000))

    rdir2 = sewerrat.retrieve_directory(subpath, url=url, cache=cache, force_remote=True)
    assert rdir == rdir2
    with open(os.path.join(rdir2, "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"

    # Trying with multiple cores.
    cache = tempfile.mkdtemp()
    rdir2 = sewerrat.retrieve_directory(mydir, url=url, cache=cache, force_remote=True, concurrent=2)
    with open(os.path.join(rdir2, "diet", "metadata.json"), "r") as f:
        meta = json.load(f)
        assert meta["meal"] == "lunch"
