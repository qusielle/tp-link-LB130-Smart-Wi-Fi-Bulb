#!/usr/bin/env python3
"""Control class for TP-Link A19-LB130 RBGW WiFi bulb."""

import datetime
import socket
import json
import logging
import time


class LB130(object):
    """Methods for controlling the LB130 bulb."""

    encryption_key = 0xAB

    min_brightness = 1
    max_brightness = 100
    min_hue = 0
    max_hue = 360
    min_saturation = 0
    max_saturation = 100
    min_transition_period = 0
    max_transition_period = 100000
    min_color_temp = 2500
    max_color_temp = 9000

    __udp_ip = None
    __udp_port = 9999
    __socket_timeout = 0.5
    __max_retry = 5
    __on_off = 0
    __transition_period = 0
    __hue = 0
    __saturation = 0
    __brightness = 0
    __color_temp = 0
    __mode = ''

    # Force quering the status every time when get property
    force_update = False

    __alias = ''
    device_id = ''
    lamp_beam_angle = 0
    min_voltage = 0
    max_voltage = 0
    wattage = 0
    incandescent_equivalent = 0
    max_lumens = 0
    color_rendering_index = 0

    def __init__(self, ip_address):
        """Initialise the bulb with an IP address."""

        split_ip = tuple(int(i) if i.isdigit() else -1 for i in ip_address.split('.'))
        valid_ip = (len(split_ip) == 4) and all(
            True if 0 <= i <= 255 else False for i in split_ip
        )
        if not valid_ip:
            raise ValueError('Invalid bulb IP address.')

        self.__udp_ip = ip_address

        # Parse the sysinfo JSON message to get the
        # status of the various parameters.
        self.__update_self_status()

        # Parse the light details JSON message to get the
        # status of the various parameters.
        data = self.light_details()

        light_details_data = data['smartlife.iot.smartbulb.lightingservice']['get_light_details']
        self.lamp_beam_angle = int(light_details_data['lamp_beam_angle'])
        self.min_voltage = int(light_details_data['min_voltage'])
        self.max_voltage = int(light_details_data['max_voltage'])
        self.wattage = int(light_details_data['wattage'])
        self.incandescent_equivalent = int(light_details_data['incandescent_equivalent'])
        self.max_lumens = int(light_details_data['max_lumens'])
        self.color_rendering_index = str(light_details_data['color_rendering_index'])

    def __str__(self):
        return (
            '<LB130'
            f' {self.__udp_ip}'
            f' {"ON" if self.__on_off else "OFF"}'
            f' transition_period:{self.__transition_period}'
            f' hue:{self.__hue}'
            f' saturation:{self.__saturation}'
            f' brightness:{self.__brightness}'
            f' color_temp:{self.__color_temp}'
            f'>'
        )

    def transite_light_state(self, **kwargs):
        """
        Update one or more bulb's properties at one time to achieve a smooth
        transition between states using the bulb's hardware in a natural way.

        Refer to class constants for valid ranges for arguments.

        Keyword args:
            transition_period: Transition duration in milliseconds.
            on_off: Target power state. True for ON, False for OFF.
            hue: Target hue.
            saturation: Target saturation.
            brightness: Target brightness.
            color_temp: Target color temperature.
            mode: Target bulb operational mode: `normal` or `circadian`.
            synchronous: Put sleep until the end of transition_period if True.
        """
        data = {'smartlife.iot.smartbulb.lightingservice': {
            'transition_light_state': {'ignore_default': 1}
        }}
        state = data['smartlife.iot.smartbulb.lightingservice']['transition_light_state']

        if ('hue' in kwargs or 'saturation' in kwargs):
            if 'color_temp' in kwargs:
                raise ValueError('color_temp should not be set with hue or saturation.')
            kwargs['color_temp'] = 0

        if 'transition_period' in kwargs:
            self.transition_period = kwargs['transition_period']
        state['transition_period'] = self.__transition_period

        def state_setter(arg, arg_type, checker):
            if arg in kwargs:
                casted_arg = arg_type(kwargs[arg])
                if not checker(casted_arg):
                    raise ValueError(arg + ' is wrong.')
                setattr(self, '__' + arg, casted_arg)  # self.__arg = kwargs['arg']
                state[arg] = casted_arg

        state_setter('on_off', int, lambda x: x in (0, 1))
        state_setter('hue', int, lambda x: self.min_hue <= x <= self.max_hue)
        state_setter('saturation', int, lambda x: self.min_saturation <= x <= self.max_saturation)
        state_setter('brightness', int, lambda x: self.min_brightness <= x <= self.max_brightness)
        state_setter(
            'color_temp', int, lambda x: self.min_color_temp <= x <= self.max_color_temp or x == 0
        )
        state_setter('mode', str, lambda x: x in ('normal', 'circadian'))

        if kwargs.get('synchronous'):
            start_time = time.time()

        self.__fetch_dict(data)

        if kwargs.get('synchronous'):
            time.sleep(self.__transition_period / 1000.0 - (time.time() - start_time))

    def status(self):
        """Get the connection status from the bulb."""
        return json.dumps(self.__update_self_status())

    def light_details(self):
        """Get the light details from the bulb."""
        return self.__fetch_dict(
            {'smartlife.iot.smartbulb.lightingservice': {'get_light_details': ''}}
        )

    def on(self):
        """Set the bulb to an ON state."""
        self.transite_light_state(on_off=1)

    def off(self):
        """Set the bulb to an OFF state."""
        self.transite_light_state(on_off=0)

    def ison(self):
        """Check if bulb is on."""
        self.__update_self_status()
        return self.__on_off

    def reboot(self):
        """Reboot the bulb."""
        self.__fetch_dict({'smartlife.iot.common.system': {'reboot': {'delay': 1}}})

    @property
    def alias(self):
        """Get the device alias."""
        return self.__alias

    @alias.setter
    def alias(self, name):
        """Set the device alias."""
        if not isinstance(name, str):
            ValueError('name should be str.')
        self.__fetch_dict({'smartlife.iot.common.system': {'set_dev_alias': {'alias': name}}})

    @property
    def time(self):
        """Get the date and time from the device."""
        response = self.__fetch_dict({'smartlife.iot.common.timesetting': {'get_time': {}}})
        get_time = response['smartlife.iot.common.timesetting']['get_time']

        return datetime.datetime(
            get_time['year'],
            get_time['month'],
            get_time['mday'],
            get_time['hour'],
            get_time['min'],
            get_time['sec'],
        )

    @time.setter
    def time(self, date):
        """Set the date and time on the device."""
        if isinstance(date, datetime.datetime):
            self.__fetch_dict({'smartlife.iot.common.timesetting': {
                'set_time': {
                    'year': date.year,
                    'month': date.month,
                    'mday': date.day,
                    'hour': date.hour,
                    'min': date.minute,
                    'sec': date.second,
                }
            }})
        else:
            raise ValueError('Invalid type: must pass a datetime object')
        return

    @property
    def timezone(self):
        """Get the timezone from the device."""
        data = self.__fetch_dict({'smartlife.iot.common.timesetting': {'get_timezone': {}}})
        timezone = data['smartlife.iot.common.timesetting']['get_timezone']['index']
        return timezone

    @timezone.setter
    def timezone(self, timezone):
        """Set the timezone on the device."""
        if timezone >= 0 and timezone <= 109:
            date = self.time
            self.__fetch_dict({'smartlife.iot.common.timesetting': {
                'set_timezone': {
                    'index': timezone,
                    'year': date.year,
                    'month': date.month,
                    'mday': date.day,
                    'hour': date.hour,
                    'min': date.minute,
                    'sec': date.second,
                }
            }})
        else:
            raise ValueError('Timezone out of range: 0 to 109')
        return

    @property
    def transition_period(self):
        """Get the bulb transition period."""
        return self.__transition_period

    @transition_period.setter
    def transition_period(self, period):
        """Set the bulb transition period."""
        if self.min_transition_period <= period <= self.max_transition_period:
            self.__transition_period = period
        else:
            raise ValueError(
                '`transition_period` is out of range:'
                f' {self.min_transition_period} to {self.max_transition_period}'
            )

    @property
    def hue(self):
        """Get the bulb hue."""
        if self.force_update:
            self.__update_self_status()
        return self.__hue

    @hue.setter
    def hue(self, hue):
        """Set the bulb hue."""
        self.transite_light_state(hue=hue)

    @property
    def saturation(self):
        """Get the bulb saturation."""
        if self.force_update:
            self.__update_self_status()
        return self.__saturation

    @saturation.setter
    def saturation(self, saturation):
        """Set the bulb saturation."""
        self.transite_light_state(saturation=saturation)

    @property
    def brightness(self):
        """Get the bulb brightness."""
        if self.force_update:
            self.__update_self_status()
        return self.__brightness

    @brightness.setter
    def brightness(self, brightness):
        """Set the bulb brightness."""
        self.transite_light_state(brightness=brightness)

    @property
    def temperature(self):
        """Get the bulb color temperature."""
        if self.force_update:
            self.__update_self_status()
        return self.__color_temp

    @temperature.setter
    def temperature(self, temperature):
        """Set the bulb color temperature."""
        self.transite_light_state(color_temp=temperature)

    @property
    def mode(self):
        """Get the bulb color mode."""
        if self.force_update:
            self.__update_self_status()
        return self.__mode

    @mode.setter
    def mode(self, mode):
        """Set the bulb color mode."""
        self.transite_light_state(mode=mode)

    @property
    def hsb(self):
        """Get the bulb hue, saturation, and brightness."""
        return (self.__hue, self.__saturation, self.__brightness)

    @hsb.setter
    def hsb(self, hsb):
        """Set the bulb hue, saturation, and brightness."""
        try:
            hue, saturation, brightness = hsb
        except ValueError:
            raise ValueError('Pass an iterable with hue, saturation, and brightness')

        self.transite_light_state(hue=hue, saturation=saturation, brightness=brightness)

    # Private Methods

    @staticmethod
    def __encrypt(value, key):
        """Encrypt the command string."""
        valuelist = list(value)

        for i in range(len(valuelist)):
            var = ord(valuelist[i])
            valuelist[i] = chr(var ^ int(key))
            key = ord(valuelist[i])
        return bytearray(''.join(valuelist).encode('latin_1'))

    @staticmethod
    def __decrypt(value, key):
        """Decrypt the command string."""
        valuelist = list(value.decode('latin_1'))

        for i in range(len(valuelist)):
            var = ord(valuelist[i])
            valuelist[i] = chr(var ^ key)
            key = var

        return ''.join(valuelist)

    def __update_self_status(self):
        """Fetch sysinfo from the bulb and update local values."""
        data = self.__fetch_dict({'system': {'get_sysinfo': {}}})
        sysinfo_data = data['system']['get_sysinfo']
        light_state_data = sysinfo_data['light_state']
        self.__alias = sysinfo_data['alias']
        self.device_id = str(sysinfo_data['deviceId'])
        self.__on_off = int(light_state_data['on_off'])
        if not self.__on_off:
            light_state_data = light_state_data['dft_on_state']

        self.__hue = int(light_state_data['hue'])
        self.__saturation = int(light_state_data['saturation'])
        self.__brightness = int(light_state_data['brightness'])
        self.__color_temp = int(light_state_data['color_temp'])
        self.__mode = light_state_data['mode']

        return data

    def __fetch_data(self, message):
        """Fetch data from the device."""
        enc_message = self.__encrypt(message, self.encryption_key)

        for retry in range(1, self.__max_retry + 1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.__socket_timeout * retry)
                sock.sendto(enc_message, (self.__udp_ip, self.__udp_port))
                data_received = False
                dec_data = ''
                while True:
                    data, _ = sock.recvfrom(1024)  # buffer size is 1024 bytes
                    dec_data = self.__decrypt(data, self.encryption_key)
                    if '}}}' in dec_data:  # end of sysinfo message
                        data_received = True
                        break

                if data_received:
                    if '"err_code":0' in dec_data:
                        return dec_data
                    else:
                        raise RuntimeError('Bulb returned error: ' + dec_data)
                else:
                    raise socket.timeout()
            except socket.timeout:
                logging.debug('Socket timed out. Try %d/%d' % (retry, self.__max_retry + 1))

        raise RuntimeError('Error connecting to bulb')

    def __fetch_dict(self, data):
        """Fetch dict from the device. Return value is a dict too."""
        if not isinstance(data, dict):
            raise ValueError('data should be dict.')
        message = json.dumps(data)
        return json.loads(self.__fetch_data(message))
