#!/bin/bash 
set -x
set -e
# exec startx &
# sleep 3
cd "$(dirname "$0")"
source .venv/bin/activate

export DISPLAY=:0.0
RESOLUTION=$(<resolution)
# HD 1920,1080
# RESOLUTION=1920,1080
# 4K 3840,2160
# RESOLUTION=3840,2160
echo "RESOLUTION: '$RESOLUTION'"
python3 app.py --window-size $RESOLUTION --hide-url --high-quality --volume 0.55 --logo-path /home/default/logo.png --admin-password pass.1234

