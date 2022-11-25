# EETC Utils

Library of useful Python code to help with development of software under the EETC umbrella.

This library will contain all code that we come up with during development of other projects
that we think can be reused in more than one project continuously.

# Installation
```commandline
pip install eetc-utils
```

# Development

## System requirements
To run the project locally and work on it, you need the following:
- Python 3.8+

## Project setup
```commandline
sudo apt-get install build-essential
make update_and_install_python_requirements
```

## Adding a new Python package
1. Add the package name to `requirements.in`
2. Run:
```commandline
make update_and_install_python_requirements
```

## Publishing new package versions to PyPi
1. Update `[build_system]` section in `pyproject.toml` in case new dependencies are added or existing dependency versions were updated.
2. Update `version` field in `[project]` section in `pyproject.toml` whenever there is a new change to the project.
3. Build the project using command:
```commandline
python -m build
```
4. Publish package on PyPi Test, run command:
```commandline
python -m twine upload --repository testpypi dist/*
```
5. If everything is ok on PyPi Test, publish on "real" PyPi using the command:
```commandline
python -m twine upload --repository pypi dist/*
```
