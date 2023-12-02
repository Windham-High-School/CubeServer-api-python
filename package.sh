#!/usr/bin/env bash

git submodule update --remote --init --recursive

wget https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_IRRemote/main/adafruit_irremote.py -O ./lib/adafruit_irremote.py
wget https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_BMP280/main/adafruit_bmp280.py -O ./lib/adafruit_bmp280.py
wget https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_NeoPixel/main/neopixel.py -O ./lib/neopixel.py

./update_version.sh
zip cubeserver-api-python.zip -r lib/ boot.py code.py 2>&1 > /dev/null
echo cubeserver-api-python.zip
