#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Command-line interface for tplight module'''

import argparse
import json
import logging
import pprint
import time

import tplight

def main():
    p = argparse.ArgumentParser()
    p.add_argument('address', help='IP of bulb')
    p.add_argument('--transition-period', '-p', type=int, help='Set transition_period between state changes')
    p.add_argument('--temperature', '-t', type=int, help='Set bulb white color temperature')
    p.add_argument('--hue', type=int, help='Set bulb color hue')
    p.add_argument('--saturation', type=int, help='Set bulb color saturation')
    p.add_argument('--circadian', action='store_true', help='Set bulb color mode to circadian')
    p.add_argument('--status', action='store_true', help='Get bulb status')
    p.add_argument('--time', action='store_true', help='Get bulb time')
    p.add_argument('--wait', action='store_true', help='Wait until the transition_period end')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--brightness', '-b', type=int, help='Set bulb brightness')
    group.add_argument('--brightness-offset', '-f', type=int, help='Offset the value of brightness. Positive of negative')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--switch', '-s', action='store_true', help='Switch bulb state ON/OFF')
    group.add_argument('--on', action='store_true', help='Turn on the bulb')
    group.add_argument('--off', action='store_true', help='Turn off the bulb')
    args = p.parse_args()

    light = tplight.LB130(args.address)

    new_state = {}

    if args.status:            pprint.pprint(json.loads(light.status()))
    if args.time:              print(light.time.strftime('%Y/%m/%d %H:%M:%S'))

    if args.on:                new_state['on_off'] = 1
    if args.off:               new_state['on_off'] = 0
    if args.switch:            new_state['on_off'] = int(not light.ison())

    if args.transition_period: new_state['transition_period'] = args.transition_period
    if args.temperature:       new_state['color_temp'] = args.temperature
    if args.hue:               new_state['hue'] = args.hue
    if args.saturation:        new_state['saturation'] = args.saturation
    if args.circadian:         new_state['mode'] = 'circadian'
    if args.brightness:        new_state['brightness'] = args.brightness
    if args.brightness_offset: new_state['brightness'] = max(light.min_brightness, min(light.max_brightness,
                                                                light.brightness + args.brightness_offset))
    if args.wait:              new_state['synchronous'] = True

    if new_state:
        light.transite_light_state(**new_state)

if __name__ == '__main__':
    main()
