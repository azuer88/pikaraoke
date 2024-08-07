#!/bin/bash 
set -x
set -e
# exec startx &
# sleep 3
cd "$(dirname "$0")/.."
source .venv/bin/activate
source scripts/check_wifi.sh

export DISPLAY=:0.0
RESOLUTION=$(<resolution)
# HD 1920,1080
# RESOLUTION=1920,1080
# 4K 3840,2160
# RESOLUTION=3840,2160
echo "RESOLUTION: '$RESOLUTION'"
if [ -f $HOME/hotspot ]; then
  HIDE_URl=""
else
  HIDE_URl="--hide-url"
fi

python3 app.py \
    --window-size $RESOLUTION $HIDE_URl \
    --high-quality \
    --volume 0.55 \
    --logo-path /home/default/logo.png \
    --admin-password pass.1234
    --background $HOME/backgrounds

