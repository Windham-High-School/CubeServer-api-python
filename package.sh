#!/usr/bin/env bash

./update_version.sh
zip -r cubeserver-api-python.zip . -x .gitignore -x ./.git 2>&1 > /dev/null
echo cubeserver-api-python.zip
