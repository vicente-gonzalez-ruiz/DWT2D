#!/bin/sh

set -x

convert $DATA/lena.png /tmp/lena.y
zoom_in_Y -l 1 -y 512 -x 512 < /tmp/lena.y | rawtopgm 1024 1024 > /tmp/lena-1024.pgm
display /tmp/lena-1024.pgm &
rm /tmp/lena.y

set +x