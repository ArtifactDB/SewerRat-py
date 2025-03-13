from typing import Optional, List, Dict, Literal
import requests
import warnings

from . import _utils as ut


def query(
    url: str,
    text: Optional[str] = None, 
    user: Optional[str] = None, 
    path: Optional[str] = None, 
    after: Optional[int] = None, 
    before: Optional[int] = None, 
    number: int = 100, 
    on_truncation: Literal["message", "warning", "none"] = "message") -> List[Dict]:
    """
    Query the metadata in the SewerRat backend based on free text, the owner,
    creation time, etc. This function does not require filesystem access.

    Args:
        url:
            String containing the URL to the SewerRat REST API.

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
            This can also be ``float("inf")`` to retrieve all available results.

        on_truncation:
            String specifying the action to take when the number of search
            results is capped by ``number``.
    
    Returns:
        List of dictionaries where each inner dictionary corresponds to a
        metadata file and contains:

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

    if on_truncation != "none":
        original_number = number
        number += 1

    stub = "/query?translate=true"
    collected = []

    while len(collected) < number:
        current_url = url + stub
        if number != float("inf"):
            current_url += "&limit=" + str(number - len(collected))

        res = requests.post(current_url, json=query)
        if res.status_code >= 300:
            raise ut.format_error(res)

        payload = res.json()
        collected += payload["results"]
        if "next" not in payload:
            break
        stub = payload["next"]

    if on_truncation != "none":
        if original_number != float("inf") and len(collected) > original_number:
            msg = "truncated query results to the first " + str(original_number) + " matches"
            if on_truncation == "warning":
                warnings.warn(msg)
            else:
                print(msg)
            collected = collected[:original_number]

    return collected
