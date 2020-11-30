#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import logging

import tplight

def long_transite(light, duration, brightness=None, color_temp=None, hue=None, saturation=None):
    '''Perform transition between bulb states with duration that exceeds maximum allowable transition_period.
    Transition will be splitted to several steps and processed sequentially.
    Input values is normalized according to the limits.
    '''
    start_end_states = {}
    if brightness is not None: start_end_states['brightness'] = (light.brightness, min(light.max_brightness, brightness))
    if color_temp is not None: start_end_states['color_temp'] = (light.temperature, min(light.max_color_temp, max(light.min_color_temp, color_temp)))
    if hue is not None: start_end_states['hue'] = (light.hue, min(light.max_hue, max(light.min_hue, hue)))
    if saturation is not None: start_end_states['saturation'] = (light.saturation, min(light.max_saturation, max(light.min_saturation, saturation)))

    duration = int(duration)
    steps = [light.max_transition_period] * (duration / light.max_transition_period)
    if duration % light.max_transition_period:
        steps.append(duration % light.max_transition_period)

    for n, current_duration in enumerate(steps, 1):
        states = {k: v[0] + (v[1] - v[0]) / len(steps) * n for k, v in list(start_end_states.items())}
        states['transition_period'] = current_duration
        states['synchronous'] = True
        if not light.ison():
            states['on_off'] = 1
        logging.debug('Step %d/%d: %s' % (n, len(steps), light))
        light.transite_light_state(**states)

def scenario_1(light, minutes_before_wakeup, max_brightness, max_temperature):
    '''There are 3 steps during the minutes_before_wakeup time:
    - Turn on bulb with minimal brightness and temperature
    - Increase brightness and temperature to the half of maximum
    - Increase brightness and temperature to the maximum
    Then start to pulse with 100% brightness and more cold light
    '''
    duration = minutes_before_wakeup * 60 * 1000

    long_transite(light, 0.5 * duration, color_temp=light.min_color_temp, brightness=1)
    long_transite(light, 0.35 * duration, color_temp=(max_temperature + light.min_color_temp) / 2, brightness=max_brightness / 2)
    long_transite(light, 0.15 * duration, color_temp=max_temperature, brightness=max_brightness)

    for i in range(200):
        light.transite_light_state(transition_period=300, color_temp=4200, brightness=100, synchronous=True)
        light.transite_light_state(transition_period=300, color_temp=max_temperature, brightness=max_brightness, synchronous=True)
        time.sleep(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('address', help='IP of bulb')
    p.add_argument('time', type=int, help='How much time is before wake up in minutes')
    p.add_argument('--debug', '-d', action='store_true', help='Enable debug output')
    p.add_argument('--max-brightness', '-p', type=int, default=60, help='Set the maximum brightness be reached at the end of scenario')
    p.add_argument('--max-temperature', '-t', type=int, default=3600, help='Set the maximum temperature be reached at the end of scenario')
    args = p.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    light = tplight.LB130(args.address)
    print(('Device alias: ' + light.alias))

    scenario_1(light, args.time, args.max_brightness, args.max_temperature)

if __name__ == '__main__':
    main()