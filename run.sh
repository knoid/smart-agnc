#!/bin/sh

cd "`dirname \"$0\"`"/src
python -m smart_agnc $*
