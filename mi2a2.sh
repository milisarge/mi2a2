#!/bin/bash
./port_oldur.sh
sudo ./sunucu.py &
sleep 2
if which xdg-open > /dev/null
then
  xdg-open http://127.0.0.1:7070/
elif which gnome-open > /dev/null
then
 gnome-open http://127.0.0.1:7070/
fi
