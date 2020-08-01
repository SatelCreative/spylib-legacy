#!/bin/bash

source config.sh

watchmedo auto-restart -d . -d .. --patterns="*.py;*.txt;*.yml;*.graphql" --recursive uvicorn -- --host 0.0.0.0 webapp.main:app
