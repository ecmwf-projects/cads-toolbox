# cads-toolbox

CADS Toolbox library provides an entry point to the CADS data and software

## Quick Start

### import the package

```python
>>> import cads_toolbox
>>> cads_toolbox.config.USE_CACHE = True  # opt-in to use the cache globally

```

### Request some data and download to a local location

```python
>>> request = [
...    "reanalysis-era5-single-levels",
...    {
...        'variable': '2m_temperature',
...        'product_type': 'reanalysis',
...        'year': '2017',
...        'month': '01',
...        'day': '01',
...        'time': '12:00',
...    }
... ]
>>> remote = cads_toolbox.catalogue.retrieve(*request)
>>> remote.download() # Uses filename on server for downloaded result
'...'
>>> remote.download(target='./test.grib') # Saves result in ./test.ext
'./test.grib'

```

### Request some data and explore polymorphism and caching

```python
>>> remote = cads_toolbox.catalogue.retrieve(*request)
>>> dataset = remote.to_xarray() # Involves download to your local cache disk (cacholote) and harmonisation of data coordinates and unit names (cgul)
>>> dataset
<xarray.Dataset>
Dimensions:  ...
>>> dataframe = remote.to_pandas() # Uses cached interim result from to_xarray so re-download is not required.

```

### Request some data, open as an xarray dataset and plot using xarray methods

```python
>>> remote = cads_toolbox.catalogue.retrieve(*request)
>>> dataset = remote.to_xarray()
>>> dataset
<xarray.Dataset>
Dimensions:  ...
>>> dataarray = dataset.to_array()  # Use xarray methods to manipulate the object
>>> dataarray
<xarray.DataArray ...
>>> dataarray.isel(time=0).plot()
<matplotlib.collections.QuadMesh object ...

```

### NOT YET IMPLEMENTED: Use the CADS toolbox service to execute large compute jobs on the CADS infrastructure

```python
>>> remote = cads_toolbox.catalogue.retrieve(*request)  # doctest: +SKIP
>>> climatology = cads_toolbox.climatology(remote, **kwargs)  # doctest: +SKIP
>>> climatology_ds = climatology.to_xarray()  # doctest: +SKIP
>>> # OR downloaded directly:
>>> climatology.download("./my_climatology.nc")  # doctest: +SKIP
'./my_climatology.nc'  # doctest: +SKIP

```

## Workflow for developers/contributors

For best experience create a new conda environment (e.g. DEVELOP) with Python 3.10:

```
conda create -n DEVELOP -c conda-forge python=3.10
conda activate DEVELOP
```

Before pushing to GitHub, run the following commands:

1. Update conda environment: `make conda-env-update`
1. Install this package: `pip install -e .`
1. Sync with the latest [template](https://github.com/ecmwf-projects/cookiecutter-conda-package) (optional): `make template-update`
1. Run quality assurance checks: `make qa`
1. Run tests: `make unit-tests`
1. Run the static type checker: `make type-check`
1. Build the documentation (see [Sphinx tutorial](https://www.sphinx-doc.org/en/master/tutorial/)): `make docs-build`

## License

```
Copyright 2022, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
