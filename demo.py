#!/usr/bin/env python3

"""
Demo for the TP-Link A19-LB130 RBGW WiFi bulb
"""


import time
from tplight import LB130


def main():
    """
    Main program function
    """

    # create an instance of the light with its IP address
    light = LB130('10.0.0.130')

    # fetch the details for the light
    print(f'Device ID: {light.device_id}')
    print(f'Alias: {light.alias}')
    print(f'Wattage: {str(light.wattage)}')

    # set the transition period for any changes to 1 seconds
    light.transition_period = 0

    # set the brightness to 50%
    light.brightness = 50
    time.sleep(2)

    # set the saturation to 100%
    light.saturation = 90
    time.sleep(2)

    # cycle through the colours
    light.hue = 0
    time.sleep(1)
    light.hue = 60
    time.sleep(1)
    light.hue = 120
    time.sleep(1)
    light.hue = 180
    time.sleep(1)
    light.hue = 240
    time.sleep(1)
    light.hue = 300
    time.sleep(1)

    # set the colour to warm white and the brightness to 0
    light.temperature = 3800
    light.brightness = 0


if __name__ == '__main__':
    main()
