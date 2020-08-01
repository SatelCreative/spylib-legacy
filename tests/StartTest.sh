#!/bin/sh


if [ -z $DEVMODE ]; then
  docker-compose exec spylib ./StartTest.sh
else
  PYTEST='echo -e "\n######### RUN TESTS ########" && python -m pytest -vv --durations=3'
  MYPY='echo -ne "\n######### CHECK TYPING: " && MYPYOUT=`mypy --no-error-summary .`; if [ -z "$MYPYOUT" ]; then echo "OK"; else echo -e "\e[1m\e[91mFAILED\e[21m\e[39m"; echo "$MYPYOUT"; fi'
  FLAKE8='echo -ne "\n######### CHECK LINTING: " && FLAKE8OUT=`flake8`; if [ -z "$FLAKE8OUT" ]; then echo "OK"; else echo -e "\e[1m\e[91mFAILED\e[21m\e[39m"; echo "$FLAKE8OUT"; fi'
  COM="sleep 3 && $PYTEST; $MYPY; $FLAKE8"

  echo -e "\nREADY TO RUN THE CODE VALIDATION SUITE\nSave a python file to trigger the checks."
  
  source config_test.sh
  watchmedo shell-command --patterns="*.py;*.txt" --recursive\
    --command="$COM" --drop .
fi
