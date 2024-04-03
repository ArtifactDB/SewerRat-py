from typing import List, Optional
import requests
import os
import warnings
import time

from .rest_url import rest_url


def deregister(path: str, url: Optional[str] = None, wait: int = 1):
    """
    Deregister a directory from the SewerRat search index.

    Args:
        path: 
            Path to the directory to be registered.

        url:
            URL to the SewerRat REST API. This defaults to the current setting of :py:func:`~rest_url.rest_url`.

        wait:
            Number of seconds to wait for a file write to synchronise before requesting verification.

    Returns:
        On success, the directory is deregistered and nothing is returned.
    """
    path = os.path.abspath(path)
    if url is None:
        url = rest_url()

    res = requests.post(url + "/deregister/start", json = { "path": path }, allow_redirects=True)
    body = res.json()
    if res.status_code >= 400:
        raise ValueError(body["reason"])

    # If it succeeded on start, we don't need to do verification.
    if body["status"] == "SUCCESS":
        return

    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        pass

    # Sleeping for a while so that files can sync on network shares.
    time.sleep(wait)

    try:
        res = requests.post(url + "/deregister/finish", json = { "path": path }, allow_redirects=True)
        body = res.json()
        if res.status_code >= 300:
            raise ValueError(body["reason"])
    finally:
        os.unlink(target)

    return
