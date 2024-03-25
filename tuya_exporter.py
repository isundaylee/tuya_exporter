#!/usr/bin/env python3

import time
from typing import List

import click
import tinytuya
import attr
import yaml
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


@attr.s(auto_attribs=True)
class DeviceConfig:
    name: str
    ip: str
    device_id: str
    local_key: str
    version: str

    @classmethod
    def parse(cls, s) -> "DeviceConfig":
        try:
            name, ip, device_id, local_key, version = s.split(":::")
        except:
            print(s.split(':::'))
        return cls(
            name=name,
            ip=ip,
            device_id=device_id,
            local_key=local_key,
            version=version,
        )
        

class Collector:
    def __init__(self, configs: List[DeviceConfig]):
        self.configs = configs

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
        for config in self.configs:
            d = tinytuya.OutletDevice(config.device_id, config.ip, config.local_key)
            print(f"Parsing {config}")
            d.set_version(float(config.version))
            d.set_socketTimeout(2)
            d.updatedps([18, 19, 20])
            data = d.status()
            if not data.get("Error"):
                current_gauge.add_metric([config.name], float(data.get("dps", {}).get("18", data.get("dps", {}).get("21", 0))) / 1000.0)
                power_gauge.add_metric([config.name],   float(data.get("dps", {}).get("19", data.get("dps", {}).get("22", 0))) / 10.0)
                voltage_gauge.add_metric([config.name], float(data.get("dps", {}).get("20", data.get("dps", {}).get("23", 0))) / 10.0)
            else:
                print(f"Error getting data for device {config.name} {data}")

        yield current_gauge
        yield power_gauge
        yield voltage_gauge


@click.command()
@click.argument("devices", nargs=-1)
@click.option("--port", help="Port to run the Prometheus exporter on.", default=9185)
def main(devices, port):
    device_configs = [DeviceConfig.parse(d) for d in devices]
    collector = Collector(device_configs)
    REGISTRY.register(collector)
    start_http_server(port)

    while True:
        time.sleep(0.1)


if __name__ == "__main__":
    main()
