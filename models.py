from dataclasses import dataclass
from abc import ABC
from typing import Optional


class Zone(ABC):
    def __init__(self, name: str):
        self.name = name
        self.zone_type: str
        self.color: Optional[str] = None
        self.prior = False
        self.cost: int = 1
        self.max_drones: int = 1


class NormalZone(Zone):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.zone_type: str = "normal"
        self.color: Optional[str] = None
        self.prior = False
        self.cost: int = 1
        self.max_drones: int = 1
        self.connection: list['Connection'] = []


class RestrictedZone(Zone):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.zone_type: str = "restricted"
        self.color: Optional[str] = None
        self.prior = False
        self.cost: int = 2
        self.max_drones: int = 1
        self.connection: list['Connection'] = []


class PriorityZone(Zone):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.zone_type: str = "priority"
        self.color: Optional[str] = None
        self.prior = True
        self.cost: int = 1
        self.max_drones: int = 1
        self.connection: list['Connection'] = []


class BlockedZone(Zone):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name
        self.zone_type: str = "blocked"
        self.color: Optional[str] = None
        self.prior = False
        self.cost: int = 0
        self.max_drones: int = 0
        self.connection: list['Connection'] = []


class Connection():
    def __init__(self, zone_a: Zone = None, zone_b: Zone = None):
        self.zone_type: str = "connection"
        self.color: Optional[str] = None
        self.cost: int = 1
        self.max_drones: int = 1
        self.zone_a = zone_a
        self.zone_b = zone_b


@dataclass
class GameMap:
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zone_dict: dict[str, Zone]
    connections: list[Connection]
