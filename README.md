# Tuya Exporter

This is a very bare-bone exporter for exporting information from Tuya IoT
smart plugs that exports the following gauges:

- `tuya_consumption_current` (in amps)
- `tuya_consumption_power` (in watts)
- `tuya_consumption_voltage` (in volts)

I have only tested this with [these
plugs](https://www.amazon.com/gp/product/B07CVPKD8Z/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1).
But it might work with other similar Tuya plugs too.

## Usage

You can either run `tuya_exporter.py` directly or run it via Docker using the
`isundaylee/tuya_exporter` image. In either case, pass the device
configuration as arguments on the command line with this format:

```
$ tuya_exporter.py <name1>:<ip1>:<device_id1>:<local_key1> \
    <name2>:<ip2>:<device_id2>:<local_key2> \
    ...
```

You can specify anything you like as the name - it shows up as part of the
Prometheus labels. How to retrieve device IP/ID/local key depends on your
particular plug model. Search the Internet for the most up-to-date way to
retrieve those information (e.g. [the tutorial
here](https://github.com/iRayanKhan/homebridge-tuya/wiki/Get-Local-Keys-for-your-devices)).

For my test plugs, device IDs are 22-character alphanumeric strings, and
local keys are 16-character alphanumeric strings. But they might be different
for your plugs.

## Changelog

- v0.0.2
    - Support local keys with `:` in them.
