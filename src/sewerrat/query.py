from typing import Optional, List
import requests

from .rest_url import rest_url


def query(text: Optional[str] = None, user: Optional[str] = None, path: Optional[str] = None, after: Optional[int] = None, before: Optional[int] = None, number: int = 100, url: Optional[str] = None) -> List:
    """
    Query the metadata in the SewerRat backend based on free text, the owner, creation time, etc.

    Args:
        text:
            String containing a free-text query, following the syntax described
            `here <https://github.com/ArtifactDB/SewerRat#Using-a-human-readable-text-query-syntax>`_.
            If None, no filtering is applied based on the metadata text.

        user:
            String containing the name of the user who generated the metadata.
            If None, no filtering is applied based on the user.

        path:
            String containing any component of the path to the metadata file.
            If None, no filtering is applied based on the path.

        after:
            Integer containing a Unix time in seconds, where only files newer
            than ``after`` will be retained. If None, no filtering is applied
            to remove old files.

        before:
            Integer containing a Unix time in seconds, where only files older
            than ``before`` will be retained. If None, no filtering is applied
            to remove new files.

        number:
            Integer specifying the maximum number of results to return.

        url:
            String containing the URL to the SewerRat REST API.
    
    Returns:
        List of lists where each inner list corresponds to a metadata file and contains:

        - ``path``, a string containing the path to the file.
        - ``user``, the identity of the file owner.
        - ``time``, the Unix time of most recent file modification.
        - ``metadata``, a list representing the JSON contents of the file.
    """
    conditions = []

    if text is not None:
        conditions.append({ "type": "text", "text": text })

    if user is not None:
        conditions.append({ "type": "user", "user": user })

    if path is not None:
        conditions.append({ "type": "path", "path": path })

    if after is not None:
        conditions.append({ "type": "time", "time": int(after), "after": True })

    if before is not None:
        conditions.append({ "type": "time", "time": int(before) })

    if len(conditions) > 1:
        query = { "type": "and", "children": conditions }
    elif len(conditions) == 1:
        query = conditions[0]
    else:
        raise ValueError("at least one search filter must be present")

    stub = "/query?translate=true&limit=" + str(number)
    collected = []
    if url is None:
        url = rest_url()

    while len(collected) < number:
        res = requests.post(url + stub + "&limit=" + str(number - len(collected)), json=query)
        payload = res.json()
        if res.status_code >= 400:
            raise ValueError(payload["reason"])

        collected += payload["results"]
        if "next" not in payload:
            break
        stub = payload["next"]

    return collected
