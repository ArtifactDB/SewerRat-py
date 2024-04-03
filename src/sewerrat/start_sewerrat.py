from typing import Optional, Tuple
import appdirs
import platform
import tempfile
import subprocess
import requests
import socket
import shutil
import os
import time

from .rest_url import rest_url


test_api_process = None
test_api_port = None
test_api_old_url = None


def start_sewerrat(db: Optional[str] = None, port: Optional[int] = None, set_url: bool = True) -> Tuple[bool, int]:
    """
    Start a test SewerRat service.

    Args:
        db: 
            Path to a SQLite database. If None, one is automatically created.

        port:
            An available port. If None, one is automatically chosen.

        set_url:
            Whether to set :py:func:`~rest_url.rest_url` to the URL of the test service.

    Returns:
        A tuple indicating whether a new test service was created (or an existing instance
        was re-used), and the port number of said service.
    """
    global test_api_port
    global test_api_old_url

    if test_api_process is not None:
        return False, test_api_port

    exe = _acquire_sewerrat_binary()
    _initialize_sewerrat_process(exe, db, port)

    if set_url:
        test_api_old_url = rest_url("http://0.0.0.0:" + str(test_api_port))

    time.sleep(1) # give it some time to spin up.
    return True, test_api_port


def _acquire_sewerrat_binary():
    sysname = platform.system()
    if sysname == "Darwin":
        OS = "darwin"
    elif sysname == "Linux":
        OS = "linux"
    else:
        raise ValueError("unsupported operating system '" + sysname + "'")

    sysmachine = platform.machine()
    if sysmachine == "arm64":
        arch = "arm64"
    elif sysmachine == "x86_64":
        arch = "amd64"
    else:
        raise ValueError("unsupported architecture '" + sysmachine + "'")

    cache = appdirs.user_data_dir("SewerRat", "aaron")
    desired = "SewerRat-" + OS + "-" + arch
    exe = os.path.join(cache, desired)

    if not os.path.exists(exe):
        url = "https://github.com/ArtifactDB/SewerRat/releases/download/latest/" + desired

        os.makedirs(cache, exist_ok=True)
        tmp = exe + ".tmp"
        with requests.get(url, stream=True) as r:
            with open(tmp, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        os.chmod(tmp, 0o755)

        # Using a write-and-rename paradigm to provide some atomicity. Note
        # that renaming doesn't work across different filesystems so in that
        # case we just fall back to copying.
        try:
            shutil.move(tmp, exe)
        except:
            shutil.copy(tmp, exe)

    return exe
   

def _initialize_sewerrat_process(exe: str, db: Optional[str], port: Optional[int]):
    if port is None:
        with socket.socket(socket.AF_INET) as s:
            s.bind(('0.0.0.0', 0))
            port = s.getsockname()[1]

    if db is None:
        host = tempfile.mkdtemp()
        db = os.path.join(host, "index.sqlite3")

    global test_api_port
    global test_api_process
    test_api_port = port
    test_api_process = subprocess.Popen([ exe, "-db", db, "-port", str(port) ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return


def stop_sewerrat():
    """
    Stop any existing SewerRat test service. This will also reset any URL that
    was modified by :py:func:`~start_sewerrat`. If no test service was running,
    this function is a no-op.
    """
    global test_api_process
    global test_api_port
    global test_api_old_url

    if test_api_process is not None:
        test_api_process.terminate()
        test_api_process = None
        test_api_port = None
        if test_api_old_url is not None:
            rest_url(test_api_old_url)
            test_api_old_url = None
    return
