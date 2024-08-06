import requests
import os


def format_error(res):
    ctype = res.headers["content-type"]
    if ctype == "application/json":
        info = res.json()
        return requests.HTTPError(res.status_code, info["reason"])
    elif ctype == "text/plain":
        return requests.HTTPError(res.status_code, res.text)
    else:
        return requests.HTTPError(res.status_code)


def clean_path(path: str) -> str:
    # Don't use os.path.abspath, as this calls normpath; you would end up
    # resolving symlinks that the user wants to respect, e.g., for mounted
    # drives with aliased locations to network shares. Rather, we just do the
    # bare minimum required to obtain a clean absolute path, analogous to
    # Golang's filepath.Clean().
    if not path.startswith('/'):
        path = os.getcwd() + "/" + path

    components = path.split("/")
    keep = []
    for comp in components:
        if comp == "..":
            if len(keep):
                keep.pop()
        elif comp == "":
            # no-op, it's a redundant '//' or we're at the start.
            pass
        elif comp == ".":
            # no-op as well.
            pass
        else:
            keep.append(comp)

    keep = [""] + keep # add back the root.
    return '/'.join(keep)
