#!/usr/bin/env bash

VERSION=$(cat ./version.txt)
VERSION_STR="__version__ = \"$VERSION\""

echo $VERSION_STR > ./servercom/_version.py
