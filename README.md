# Welcome to pooch-doi

[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ssciwr/pooch-doi/ci.yml?branch=main)](https://github.com/ssciwr/pooch-doi/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/pooch-doi/badge/)](https://pooch-doi.readthedocs.io/)
[![codecov](https://codecov.io/gh/ssciwr/pooch-doi/branch/main/graph/badge.svg)](https://codecov.io/gh/ssciwr/pooch-doi)

## Installation

The Python package `pooch_doi` can be installed from PyPI:

```
python -m pip install pooch_doi
```

## Development installation

If you want to contribute to the development of `pooch_doi`, we recommend
the following editable installation from this repository:

```
git clone git@github.com:ssciwr/pooch-doi.git
cd pooch-doi
python -m pip install --editable .[tests]
```

Having done so, the test suite can be run using `pytest`:

```
python -m pytest
```

## Acknowledgments

This repository was set up using the [SSC Cookiecutter for Python Packages](https://github.com/ssciwr/cookiecutter-python-package).
