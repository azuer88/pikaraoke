#!/bin/bash
set -x
set -e
# remove Hotstop config 
HOTSPOT_CONFIG=/etc/NetworkManager/system-connections/Hotspot.nmconnection
if sudo test -f $HOTSPOT_CONFIG; then
    sudo rm $HOTSPOT_CONFIG

    # and disable hotspot
    # sudo nmcli device disconnect wlan0
    # sudo nmcli device up wlan0
    sleep 2
fi

INTF=$(</sys/class/net/wlan0/operstate)
# INTF=$(</sys/class/net/end0/operstate)
FILENAME=$HOME/hotspot

SSID=pikaraoke_wifi
PASSWD=mokantako

rm -f $FILENAME
if [ $INTF == "down" ]; then 
   echo "Interface is down"
   echo "WIFI:T:WPA;S:$SSID;P:$PASSWD;H:false;;" > $FILENAME
   sudo nmcli device wifi hotspot ssid $SSID password $PASSWD
   source $HOME/pikaraoke/.venv/bin/activate 
   qr --factory=png --output=$HOME/wifi.png < $FILENAME
else
   rm -f $HOME/wifi.png
   echo "Interface is up"
fi

