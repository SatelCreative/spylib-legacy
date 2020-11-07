#!/bin/sh

source config_test.sh
export PYTHONPATH=/python/app/spylib

watchmedo auto-restart --patterns="/python/app/*.yml" --recursive python -- -m mkdocs serve
