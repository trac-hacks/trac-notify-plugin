#!/bin/bash

set -x
set -e
rm -Rf build 
rm -Rf dist

python setup.py bdist_egg
cp dist/*.egg /usr/share/trac/plugins
