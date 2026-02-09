from dataclasses import dataclass

@dataclass(frozen=True)
class BboxInformation:
    serial_number: str
    model_name: str
    software_version: str

@dataclass(frozen=True)
class BboxNetwork:
    current_bandwidth: int
    max_bandwidth: int
    occupation_bandwidth: int

@dataclass(frozen=True)
class BboxHost:
    hostname: str
    ip_address: str
    mac_address: str
    manufacturer: str
    model_name: str
    software_version: str
    is_connected: bool

@dataclass(frozen=True)
class BboxData:
    information: BboxInformation
    hosts: list[BboxHost]

    def get_host(self, mac_address: str) -> BboxHost | None:
        return next((host for host in self.hosts if host.mac_address == mac_address), None)

    def is_host_connected(self, mac_address: str) -> bool:
        host = next((host for host in self.hosts if host.mac_address == mac_address), None)
        return host.is_connected if host is not None else False