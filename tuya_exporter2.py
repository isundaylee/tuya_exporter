#!/usr/bin/env python3

import time
import json
from typing import List

import click
import tinytuya
import attr
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


class Collector:
    def __init__(self, devices, config_file):
        self.devices = devices
        self.config_file = config_file
        try:
            config = open(self.config_file)
            self.configs = json.load(config)
            config.close()
        except (Exception, e):
            print >> sys.stderr, "does not exist"
            sys.exit(1)

    def config_filter(self, pair):
        if pair["id"] in self.devices:
            return True
        else:
            return False


    def collect(self):
        current_gauge = GaugeMetricFamily(
            "tuya_consumption_current", "Current in amps.", labels=["name"]
        )
        power_gauge = GaugeMetricFamily(
            "tuya_consumption_power", "Power in watts.", labels=["name"]
        )
        voltage_gauge = GaugeMetricFamily(
            "tuya_consumption_voltage", "Voltage in volts.", labels=["name"]
        )
        for config in filter(self.config_filter, self.configs):
            if not config["ip"]:
                print(f"Invalid device {config['id']}")
                continue
            print(f"Parsing {config['name']}")
            d = tinytuya.OutletDevice(config["id"], config["ip"], config["key"])
            current_divisor = 1000.0
            power_divisor = 10.0
            voltage_divisor = 10.0
            if config["category"] == "cz":
                dps = [18, 19, 20]
            elif config["category"] == "wk":
                dps = [108, 109, 110]
                current_divisor = 1000.0
                power_divisor = 100.0
                voltage_divisor = 100.0
            else:
                dps = [21, 22, 23]
            d.set_version(float(config["version"]))
            d.set_socketTimeout(2)
            d.updatedps(dps)
            data = d.status()
            if not data.get("Error"):
                current_gauge.add_metric([config["name"]], float(data.get("dps", {}).get(str(dps[0]),  0)) / current_divisor)
                power_gauge.add_metric([config["name"]],   float(data.get("dps", {}).get(str(dps[1]),  0)) / power_divisor)
                voltage_gauge.add_metric([config["name"]], float(data.get("dps", {}).get(str(dps[2]),  0)) / voltage_divisor)
            else:
                print(f"Error getting data for device {config['name']} {data}")
        yield current_gauge
        yield power_gauge
        yield voltage_gauge


@click.command()
@click.option("--config", "-c", help="devices.json configuration file", default="devices.json")
@click.option("--devices", "-d", help="Device ID to parse", multiple=True)
@click.option("--port", "-p", help="Port to run the Prometheus exporter on.", default=9185)
def main(devices, port, config):
    collector = Collector(devices=devices, config_file=config)
    REGISTRY.register(collector)
    start_http_server(port)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
