#!/bin/sh

source config_test.sh
export PYTHONPATH=/python/app/spylib
python -m mkdocs serve
