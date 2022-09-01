#!/bin/sh

chromium-browser localhost/ModbusPV?ciosc --kiosk &

cd $(dirname "$0")/Server

./Server.py
