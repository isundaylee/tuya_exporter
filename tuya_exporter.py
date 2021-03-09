#!/usr/bin/env python3

import time
from typing import List

import click
import tinytuya
import attr
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY


@attr.s(auto_attribs=True)
class DeviceConfig:
    name: str
    ip: str
    device_id: str
    local_key: str

    @classmethod
    def parse(cls, s) -> "DeviceConfig":
        name, ip, device_id, local_key = s.split(":")
        return cls(
            name=name,
            ip=ip,
            device_id=device_id,
            local_key=local_key,
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
            d.set_version(3.3)
            d.updatedps([18, 19, 20])
            data = d.status()
            current_gauge.add_metric([config.name], float(data["dps"]["18"]) / 1000.0)
            power_gauge.add_metric([config.name], float(data["dps"]["19"]) / 10.0)
            voltage_gauge.add_metric([config.name], float(data["dps"]["20"]) / 10.0)
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
