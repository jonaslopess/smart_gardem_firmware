#!/bin/sh
#launcher.sh

cd /
cd home/pi/Desktop/horta
git pull
cd home/pi/Desktop/horta/firmware
sudo python3 horta-coleta-dados.py &
cd home/pi/Desktop/horta/dashboard
sudo ng serve &
cd /

