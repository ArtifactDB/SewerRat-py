import requests
import os
import time

from . import _utils as ut


def deregister(path: str, url: str, retry: int = 3, wait: float = 1):
    """
    Deregister a directory from the SewerRat search index. It is assumed that
    this directory is world-readable and that the caller has write access to
    it; or, the directory does not exist.

    Args:
        path: 
            Path to the directory to be registered.

        url:
            URL to the SewerRat REST API. 

        retry:
            Deprecated, ignored.

        wait:
            Deprecated, ignored.
    """
    path = ut.clean_path(path)
    res = requests.post(url + "/deregister/start", json = { "path": path }, allow_redirects=True)
    if res.status_code >= 300:
        raise ut.format_error(res)

    # If it succeeded on start, we don't need to do verification.
    body = res.json()
    if body["status"] == "SUCCESS":
        return

    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        pass

    try:
        res = requests.post(url + "/deregister/finish", json = { "path": path }, allow_redirects=True)
        if res.status_code >= 300:
            raise ut.format_error(res)
    finally:
        os.unlink(target)

    return
