<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/SewerRat.svg?branch=main)](https://cirrus-ci.com/github/<USER>/SewerRat)
[![ReadTheDocs](https://readthedocs.org/projects/SewerRat/badge/?version=latest)](https://SewerRat.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/SewerRat/main.svg)](https://coveralls.io/r/<USER>/SewerRat)
[![PyPI-Server](https://img.shields.io/pypi/v/SewerRat.svg)](https://pypi.org/project/SewerRat/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/SewerRat.svg)](https://anaconda.org/conda-forge/SewerRat)
[![Monthly Downloads](https://pepy.tech/badge/SewerRat/month)](https://pepy.tech/project/SewerRat)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/SewerRat)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# Python interface to the SewerRat API

## Overview

The **sewerrat** package implements an Python client for the [API of the same name](https://github.com/ArtifactDB/SewerRat).
This allows users to easily query the SewerRat search index, register or deregister their own directories in the index, and quickly save and load Bioconductor objects for registration.
It is assumed that the users of the **sewerrat** client and the SewerRat API itself are accessing the same shared filesystem;
this is typically the case for high-performance computing (HPC) clusters in scientific institutions.

## Registering directories

Let's mock up a directory of metadata files:

```python
import tempfile
import os

mydir = tempfile.mkdtemp()
with open(os.path.join(mydir, "metadata.json"), "w") as handle:
    handle.write('{ "first": "foo", "last": "bar" }')

os.mkdir(os.path.join(mydir, "diet"))
with open(os.path.join(mydir, "diet", "metadata.json"), "w") as handle:
    handle.write('{ "fish": "barramundi" }')
```

We can then easily register it:

```python
import sewerrat

# Only indexing metadata files named 'metadata.json'.
sewerrat.register(mydir, names=["metadata.json"])
```

Similarly, we can deregister this directory with `deregister(mydir)`.

## Searching the index

Use the `query()` function to perform free-text searches:

```python
sewerrat.query("foo")
sewerrat.query("bar%") # partial match to 'bar...'
sewerrat.query("bar% AND foo") # boolean operations
sewerrat.query("fish:bar%") # match in the 'fish' field
```

We can also search on the user, path components, and time of creation:

```python
sewerrat.query(user="LTLA") # created by myself
sewerrat.query(path="diet/") # path has 'diet/' in it

import time
sewerrat.query(after=time.time() - 3600) # created less than 1 hour ago
```

## Saving Bioconductor objects for registration

We provide some convenience methods to quickly save Bioconductor objects and associated metadata for quick registration.
For example, if we have the following objects:

```python
import biocframe
df1 = biocframe.BiocFrame({ "X": [1,2,3,4,5] })
df2 = biocframe.BiocFrame({ "Y": ["x", "y", "z"] })
df3 = biocframe.BiocFrame({ "Z": [ 1.2, 3.4, 5.6, 7.8, 9.0 ] })
```

We use the `quickSave()` function to deposit them into a directory.
(This uses the `r Biocpkg("alabaster.base")` package under the hood to create the on-disk representations.)

```python
biocdir = tempfile.mkdtemp()
sewerrat.quick_save(df1, { "description": "This has integers" }, os.path.join(biocdir, "int"))
sewerrat.quick_save(df2, { "description": "This has characters" }, os.path.join(biocdir, "char"))
sewerrat.quick_save(df3, { "description": "This has reals" }, os.path.join(biocdir, "real"))
```

Then we can just register this directory with our SewerRat API.

```python
sewerrat.register(biocdir)
```

We can now query for these objects:

```python
res = sewerrat.query("integers")
```

And once we find something we like, we can load it back in quickly:

```python
x, meta = sewerrat.quick_read(res[0]["path"])
```

## Administrator instructions

The URL to the SewerRat REST API depends on the instance and needs to be specified correctly before **sewerrat** functions can be used.
Administrators of a Python installation can achieve this by setting the `SEWERRAT_REST_URL` environment variable before **sewerrat** package load.
Developers of packages that call **sewerrat** can either pass in a URL to the `url=` argument in various **sewerrat** functions,
or they can globally set the URL via the `rest_url()` function.
