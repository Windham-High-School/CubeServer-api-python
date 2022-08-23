#!/usr/bin/env bash

zip -r cubeserver-api-circuitpython.zip . -x .git/* -x .gitignore 2>&1 > /dev/null
echo cubeserver-api-circuitpython.zip
