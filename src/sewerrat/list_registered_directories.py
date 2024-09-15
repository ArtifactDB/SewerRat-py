from typing import Optional, Union
import requests


def list_registered_directories(url: str, user: Optional[Union[str, bool]] = None):
    """
    List all registered directories in the SewerRat instance.

    Args:
        url:
            URL to the SewerRat REST API.

        user:
            Name of a user, used to filter the returned directories based on
            the user who registered them. Alternatively True, to automatically
            use the name of the current user.

    Returns:
        List of objects where each object corresponds to a registered directory
        and contains the `path` to the directory, the `user` who registered it,
        the Unix epoch `time` of the registration, and the `names` of the
        metadata files to be indexed.
    """
    if user == True:
        import getpass
        user = getpass.getuser()

    url += "/registered"
    if not user is None and user != False:
        url += "?user=" + user

    res = requests.get(url)
    if res.status_code >= 300:
        raise ut.format_error(res)
    return res.json()
