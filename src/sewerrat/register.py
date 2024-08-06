from typing import List, Optional
import requests
import os
import warnings
import time

from . import _utils as ut


def register(path: str, names: List[str], url: str, retry: int = 3, wait: int = 1):
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

        retry:
            Number of times to try to finish the registration. Larger values
            may be necessary if ``path`` is in a network share that takes some
            time to synchronise.

        wait:
            Number of seconds to wait for a file write to synchronise before
            requesting verification during each retry.
    """
    if len(names) == 0:
        raise ValueError("expected at least one entry in 'names'")

    path = ut.clean_path(path)
    res = requests.post(url + "/register/start", json = { "path": path }, allow_redirects=True)
    if res.status_code >= 300:
        raise ut.format_error(res)

    body = res.json()
    code = body["code"]
    target = os.path.join(path, code)
    with open(target, "w") as handle:
        handle.write("")

    try:
        for t in range(retry):
            # Sleeping for a while so that files can sync on network shares.
            time.sleep(wait)

            res = requests.post(url + "/register/finish", json = { "path": path, "base": names }, allow_redirects=True)
            if res.status_code < 300:
                body = res.json()
                break

            # Only looping if the status code is an Unauth failure and we're not on the last loop iteration.
            if res.status_code != 401 or t + 1 == retry:
                raise ut.format_error(res)

    finally:
        os.unlink(target)

    for comment in body["comments"]:
        warnings.warn(comment)
    return
