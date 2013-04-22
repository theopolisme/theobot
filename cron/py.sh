#!/bin/sh
# run an arbitrary Python script
PYTHONPATH=/home/theo/tools:/opt/ts/python/2.7/lib/python2.7/site-packages:/opt/ts/python/2.7/lib/python2.7:/opt/ts/python/2.7/lib/python2.7/plat-sunos5:/opt/ts/python/2.7/lib/python2.7/lib-tk:/opt/ts/python/2.7/lib/python2.7/lib-old:/opt/ts/python/2.7/lib/python2.7/lib-dynload:/opt/ts/python/2.7/lib/python2.7/site-packages:/opt/ts/python/2.7/lib/python2.7/site-packages/PIL
export PYTHONPATH
/usr/bin/python $@

