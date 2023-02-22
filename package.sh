#!/usr/bin/env bash

./update_version.sh
zip cubeserver-api-python.zip -r lib/ boot.py code.py 2>&1 > /dev/null
echo cubeserver-api-python.zip
