#!/bin/bash 
set -x
set -e
# exec startx &
# sleep 3
cd "$(dirname "$0")/.."
source .venv/bin/activate
source scripts/check_wifi.sh

export DISPLAY=:0.0
# Detect native resolution from connected display; fall back to 1080p
RESOLUTION=$(DISPLAY=:0 xrandr 2>/dev/null | awk '/\*/{print $1}' | head -1 | tr 'x' ',')
if [ -z "$RESOLUTION" ]; then
  RESOLUTION=1920,1080
fi

echo "RESOLUTION: '$RESOLUTION'" > $HOME/resolution.log
# sleep 10 
if [ -f $HOME/hotspot ]; then
  HIDE_URl=""
else
  HIDE_URl="--hide-url"
fi

python3 app.py \
    $HIDE_URl \
    --screensaver-timeout -1 \
    --volume 0.55 \
    --logo-path /home/default/logo_trans.png \
    --admin-password pass.1234 \
    --window-size $RESOLUTION \
    -l 10  > $HOME/app.log 2>&1

    # --background $HOME/backgrounds
    # --window-size $RESOLUTION \
    # --high-quality \
