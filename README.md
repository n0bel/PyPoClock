# PyPoClock
PyPoClock is an LED clock along with an information display based on the
Adafruit PyPortal.

The current version supports Date/Time, Current and forecast weather
information.

Plans are to include radar images from RainViewer.com and underlying maps from
mapbox.com.

This project was inspired and an offshoot of https://github.com/n0bel/PiClock
by the same author.

## Prerequisites
* PyPortal https://www.adafruit.com/product/4116
* DarkSky API Key https://darksky.net/dev
* Future Feature: MapBox API Key https://www.mapbox.com/signup/
  - Note that this functionality is not yet completed

## Installation
* Be sure you have the latest (version 4 or higher) of Circuit Python installed.
  - https://learn.adafruit.com/adafruit-pyportal/install-circuitpython
* Be sure you have the latest CircuitPython library Bundle installed.
  - https://learn.adafruit.com/adafruit-pyportal/circuitpython-libraries
  - Choose the 4.x version
* Copy the contents of the PyPortal folder from this repository to your PyPortal
* Rename secrets-example.py to secrets.py
* Edit secrets.py with your favorite editor to set up your information.
