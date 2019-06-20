#!/bin/sh

set -e

python3 -m pylint waylon tests
python3 -m flake8 waylon tests
python3 -m pytest
