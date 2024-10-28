from typing import Optional, Union, List, Dict
import requests
import urllib


def list_registered_directories(url: str, user: Optional[Union[str, bool]] = None, contains: Optional[str] = None, prefix: Optional[str] = None) -> List[Dict]:
    """
    List all registered directories in the SewerRat instance.

    Args:
        url:
            URL to the SewerRat REST API.

        user:
            Name of a user. If not None, this is used to filter the returned
            directories based on the user who registered them. Alternatively
            True, to automatically use the name of the current user.

        contains:
            String containing an absolute path. If not None, results are
            filtered to directories that contain this path.

        prefix:
            String containing an absolute path or a prefix thereof. If not
            None, results are filtered to directories starting with this
            string.

    Returns:
        List of objects where each object corresponds to a registered directory
        and contains the `path` to the directory, the `user` who registered it,
        the Unix epoch `time` of the registration, and the `names` of the
        metadata files to be indexed.
    """
    query = []
    if not user is None and user != False:
        if user == True:
            import getpass
            user = getpass.getuser()
        query.append("user=" + user)
    if not contains is None:
        query.append("contains_path=" + urllib.parse.quote_plus(contains))
    if not prefix is None:
        query.append("path_prefix=" + urllib.parse.quote_plus(prefix))

    url += "/registered"
    if len(query) > 0:
        url += "?" + "&".join(query)

    res = requests.get(url)
    if res.status_code >= 300:
        raise ut.format_error(res)
    return res.json()
