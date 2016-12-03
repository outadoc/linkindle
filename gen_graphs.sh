#!/bin/sh

export LINKY_USERNAME=""
export LINKY_PASSWORD=""

processimgs ()
{
    mogrify -rotate 90 -resize "600x800!" -define png:color-type=0 -define png:bit-depth=8 -dither FloydSteinberg -remap kindle_colors.gif /var/www/html/linky/*.png >> /var/log/linky.log 2>&1
}

python3 /home/iot/linkindle/linky_plot.py >> /var/log/linky.log 2>&1 && processimgs

