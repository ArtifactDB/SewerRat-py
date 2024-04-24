from typing import List, Optional
import requests
import os
import warnings
import time

from . import _utils as ut


def register(path: str, names: List[str], url: str, wait: int = 1):
    """
    Register a directory into the SewerRat search index. It is assumed that
    that the directory is world-readable and that the caller has write access.
    If a metadata file cannot be indexed (e.g., due to incorrect formatting,
    insufficient permissions), a warning will be printed but the function will
    not throw an error.

    Args:
        path: 
            Path to the directory to be registered.

        names: 
            List of strings containing the base names of metadata files inside
            ``path`` to be indexed.

        url:
            URL to the SewerRat REST API.

        wait:
            Number of seconds to wait for a file write to synchronise before
            requesting verification.
    """
    if len(names) == 0:
        raise ValueError("expected at least one entry in 'names'")

    path = os.path.abspath(path)
    if url is None:
        url = rest_url()

    res = requests.post(url + "/register/start", json = { "path": path }, allow_redirects=True)
    if res.status_code >= 300:
        raise ut.format_error(res)

    body = res.json()
    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        handle.write("")

    # Sleeping for a while so that files can sync on network shares.
    time.sleep(wait)

    try:
        res = requests.post(url + "/register/finish", json = { "path": path, "base": names }, allow_redirects=True)
        if res.status_code >= 300:
            raise ut.format_error(res)
        body = res.json()
    finally:
        os.unlink(target)

    for comment in body["comments"]:
        warnings.warn(comment)
    return
