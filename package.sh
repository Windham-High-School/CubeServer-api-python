#!/usr/bin/env bash

zip -r cubeserver-api-circuitpython.zip . -x .gitignore -x ./.git 2>&1 > /dev/null
echo cubeserver-api-circuitpython.zip
