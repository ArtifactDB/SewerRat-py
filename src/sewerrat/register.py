from typing import List, Optional
import requests
import os
import warnings
import time

from .rest_url import rest_url


def register(path: str, names: List[str] = [ "_metadata.json" ], url: Optional[str] = None, wait: int = 1):
    """
    Register a directory into the SewerRat search index.

    Args:
        path: 
            Path to the directory to be registered.

        names: 
            Array of strings containing the base names of metadata files inside ``path``.

        url:
            URL to the SewerRat REST API. This defaults to the current setting of :py:func:`~rest_url.rest_url`.

        wait:
            Number of seconds to wait for a file write to synchronise before requesting verification.

    Returns:
        On success, the directory is registered and nothing is returned.
        A warning is raised if a metadata file cannot be indexed.
    """
    if len(names) == 0:
        raise ValueError("expected at least one entry in 'names'")

    path = os.path.abspath(path)
    if url is None:
        url = rest_url()

    res = requests.post(url + "/register/start", json = { "path": path }, allow_redirects=True)
    body = res.json()
    if res.status_code >= 400:
        raise ValueError(body["reason"])
    code = body["code"]

    target = os.path.join(path, code)
    with open(target, "w") as handle:
        pass

    # Sleeping for a while so that files can sync on network shares.
    time.sleep(wait)

    try:
        res = requests.post(url + "/register/finish", json = { "path": path, "base": names }, allow_redirects=True)
        body = res.json()
        if res.status_code >= 300:
            raise ValueError(body["reason"])
    finally:
        os.unlink(target)

    for comment in body["comments"]:
        warnings.warn(comment)
    return
