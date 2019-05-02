#!/bin/sh

export LINKY_USERNAME=""
export LINKY_PASSWORD=""

OUT_DIR="/var/www/linky"
BASEDIR=$(dirname "$0")

processimgs ()
{
    mogrify \
        -rotate 90 \
        -resize "600x800!" \
        -define png:color-type=0 \
        -define png:bit-depth=8 \
        -dither FloydSteinberg \
        -remap $BASEDIR/kindle_colors.gif \
        "$OUT_DIR/*.png" >> /var/log/linky.log 2>&1
}

python3 $BASEDIR/linky_plot.py -o "$OUT_DIR" >> /var/log/linky.log 2>&1 && processimgs

