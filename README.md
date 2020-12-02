# TP-Link A19-LB130 Wi-Fi Bulb Python3 Library

The `tplight` Python library contains a class LB130 and methods for controlling
the TP-Link A19-LB130 Wi-Fi bulb.

There are two demo scripts included:
* `demo.py` shows basic usage of the library.
* `alarm.py` provides a simple scenario for a light based morning alarm.

Create an instance of the LB130 class with the IP address for the bulb:

```python
from tplight import LB130
light = LB130("10.0.0.130")
```

## Methods

`LB130.status()`

Get the connection status from the bulb.  
Returns a JSON formatted string with all of the available parameters.

---
`LB130.light_details()`

Get the light details from the bulb including min and max voltage, wattage and
colour rendering index.  
Returns a JSON formatted string with all of the available parameters.

---
`LB130.on()`

Set the bulbs state to ON.

---
`LB130.off()`

Set the bulbs state to OFF.

---
`LB130.reboot()`

Reboot the bulb.

---
`LB130.alias(name)`

Get or set the alias name for the bulb.

---
`LB130.time(date)`

Get or set the date and time on the bulb.  
Takes and returns a date as a datetime object.

---
`LB130.timezone(timezone)`

Get or set the timezone for the bulb.  
Value should be between 0 and 109.  
See [timezones.md file](timezones.md) for a list of available timezones.

---
`LB130.transition_period(period)`

Get or set the transition period for any changes made to the bulbs colour or
brightness.  
Value should be in milliseconds between 0 and 10000.

---
`LB130.hue(hue)`

Get or set the bulbs hue.  
Value should be between 0 and 360.

---
`LB130.saturation(saturation)`

Get or set the colour saturation for the bulb.  
Value should be between 0 and 100.

---
`LB130.brightness(brightness)`

Get or set the brightness.  
Value should be between 0 and 100.

---
`LB130.hsb((hue, saturation, brightness))`

Get or set the bulbs hue, saturation, and brightness.

---
`LB130.temperature(temperature)`

Get or set the colour temperature.  
Value should be between 2500 and 9000.

---
`LB130.mode(mode)`

Get or set the bulbs color mode.  
Value should be either `normal` or `circadian`.

---
`LB130.transite_light_state(**kwargs)`

Update one or more bulb's properties at one time providing target values as
keyword arguments.  
The state transition is done smoothly for `transition_period` by bulb itself.

Possible keyword arguments:
* `transition_period`: Transition duration in milliseconds.
* `on_off`: Target power state. True for ON, False for OFF.
* `hue`: Target hue.
* `saturation`: Target saturation.
* `brightness`: Target brightness.
* `color_temp`: Target color temperature.
* `mode`: Target bulb operational mode: `normal` or `circadian`.
* `synchronous`: Put sleep until the end of transition_period if True.
