#!/bin/bash

rm -rf dist
rm -rf build

# TODO: bump version

python3 setup.py sdist bdist_wheel
twine upload --repository pypi dist/*