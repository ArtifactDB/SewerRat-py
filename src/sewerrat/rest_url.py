from typing import Optional


current_url = "http://sc1lvgnplop01.sc1.roche.com:8086"


def rest_url(url: Optional[str] = None) -> str:
    """
    Get or set the URL to the SewerRat REST API.

    Args:
        url: URL to the REST API, or None.

    Returns:
        If ``url`` is missing, the current setting of the URL is returned.

        If ``url`` is supplied, it is used to replace the current setting of the URL,
        and the previous setting of the URL is returned.
    """
    global current_url
    if url is None:
        return current_url
    else:
        old = current_url
        current_url = url
        return old
