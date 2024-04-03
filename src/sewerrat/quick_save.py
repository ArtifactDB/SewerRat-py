from typing import Any, Tuple, Dict
import os
import json


def quick_save(x: Any, metadata: Dict[str, Any], path: str):
    """
    Quickly save a Bioconductor object to file in preparation for registration.
    This requires installation of the **dolomite-base** package.

    Args:
        x:
            Some Bioconductor object.

        metadata:
            A list of metadata describing the object. Any JSON-compatible
            data can be stored, in any structure; though it is conventional
            to have a ``title`` and ``description`` field.

        path: 
            Path to the directory in which to save \code{x}. Note that this
            should be world-readable if it is to be registered by
            :py:func:`~register.register`.

    Returns:
        ``x`` is saved to ``path``, with metadata saved inside ``path`` in
        a ``_metadata.json`` file.
    """
    import dolomite_base
    dolomite_base.save_object(x, path)
    with open(os.path.join(path, "_metadata.json"), "w") as handle:
        json.dump(metadata, handle, indent=4)
    return

def quick_read(path: str) -> Tuple[Any, Dict]:
    """
    Quickly read a Bioconductor object from its on-disk representation.
    This requires installation of the **dolomite-base** package.

    Args:
        path: 
            Path to a directory containing a Bioconductor object, as used
            in :py:func:`~quick_save`; or a path to the metadata file
            produced by ``quick_save()``.

    Returns:
        Tuple containing the Bioconductor object and its metadata.
    """
    if os.path.basename(path) == "_metadata.json":
        dpath = os.path.dirname(path)
        mpath = path
    else:
        dpath = path
        mpath = os.path.join(path, "_metadata.json")
    import dolomite_base
    x = dolomite_base.read_object(dpath) 
    with open(mpath, "r") as handle:
        meta = json.load(handle)
    return (x, meta)
