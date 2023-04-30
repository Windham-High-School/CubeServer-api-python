#!/usr/bin/env bash

git submodule update

VERSION=$(cat ./version.txt)
VERSION_STR="__version__ = \"$VERSION\""

echo $VERSION_STR > ./servercom/_version.py
