#!/bin/sh

chromium-browser localhost/ModbusPV/UI?kiosk --kiosk &

cd $(dirname "$0")/Server

./Server.py
