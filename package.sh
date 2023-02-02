#!/usr/bin/env bash

./update_version.sh
zip -r cubeserver-api-python.zip . -x .gitignore -x ./.git -x package.sh -x update_version.sh -x version.txt 2>&1 > /dev/null
echo cubeserver-api-python.zip
