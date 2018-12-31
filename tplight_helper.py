#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import pprint
import time

import tplight

def transite(light, duration=0, brightness=None, temperature=None, hue=None, saturation=None):
    '''
    Perform transition between bulb states (brightness, temperature, hue and/or saturation)
    with specified duration synchronously. Input values will be normalized according to the limits.
    '''
    start_time = time.time()
    duration = min(100000, max(0, duration))
    start_transition_period = light.transition_period if light.transition_period != duration * 1000 else None
    light.transition_period = duration

    if brightness is not None:  light.brightness = min(100, brightness)
    if temperature is not None: light.temperature = min(9000, max(2500, temperature))
    if hue is not None:         light.hue = min(360, max(0, hue))
    if saturation is not None:  light.saturation = min(100, max(0, saturation))

    time_left_to_sleep = duration / 1000.0 - (time.time() - start_time)
    if duration:
        logging.debug('To sleep: %f' % (time_left_to_sleep))
        time.sleep(max(0, time_left_to_sleep))
    if start_transition_period is not None:
        light.transition_period = start_transition_period

def switch_on_off(light):
    '''
    Switch ON/OFF state of the bulb.
    '''
    if light.ison():
        light.off()
        logging.debug('Bulb was turned off.')
    else:
        light.on()
        logging.debug('Bulb was turned on.')

def offset_brightness(light, offset):
    '''
    Change brightness of bulb relative to the current value.
    '''
    new_brightness = max(1, min(100, light.brightness + offset))
    logging.debug('New brightness: %d.' % (new_brightness))
    light.brightness = new_brightness

def pulse(light, duration, max_brightness_diff):
    '''
    Pulse light once with specified brightness difference and duration.
    '''
    start_brightness = light.brightness

    transite(light, duration, brightness=start_brightness + max_brightness_diff)
    transite(light, duration, brightness=start_brightness)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('address', help='IP of bulb')
    p.add_argument('--transition-period', '-p', type=int, help='Set transition_period between state changes')
    p.add_argument('--temperature', '-t', type=int, help='Set bulb white color temperature')
    p.add_argument('--hue', type=int, help='Set bulb color hue')
    p.add_argument('--saturation', type=int, help='Set bulb color saturation')
    p.add_argument('--status', action='store_true', help='Set bulb status')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--brightness', '-b', type=int, help='Set bulb brightness')
    group.add_argument('--brightness-offset', '-f', type=int, help='Offset the value of brightness. Positive of negative')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--switch', '-s', action='store_true', help='Switch bulb state ON/OFF')
    group.add_argument('--on', action='store_true', help='Turn on the bulb')
    group.add_argument('--off', action='store_true', help='Turn off the bulb')
    args = p.parse_args()

    splitted_ip = tuple(int(i) if i.isdigit() else -1 for i in args.address.split('.'))
    ip_is_valid = (len(splitted_ip) == 4) and all(True if 0 <= i <= 255 else False for i in splitted_ip)
    if not ip_is_valid:
        raise RuntimeError('IP is not valid!')

    light = tplight.LB130(args.address)

    if args.transition_period: light.transition_period = args.transition_period
    if args.temperature:       light.temperature = args.temperature
    if args.hue:               light.hue = args.hue
    if args.saturation:        light.saturation = args.saturation
    if args.brightness:        light.brightness = args.brightness
    if args.brightness_offset: offset_brightness(light, args.brightness_offset)
    if args.switch:            switch_on_off(light)
    if args.status:            pprint.pprint(json.loads(light.status()))
    if args.on:                light.on()
    if args.off:               light.off()

if __name__ == '__main__':
    main()
