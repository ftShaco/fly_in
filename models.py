from dataclasses import dataclass
from abc import ABC
from typing import Optional


class Zone(ABC):
    def __init__(self, designation: str, name: str, x: int, y: int):
        self.name = name
        self.x = x
        self.y = y
        self.zone_type: str = "undefined"
        self.designation = designation
        self.color: Optional[str] = None
        self.prior: bool = False
        self.cost: int = 1
        self.max_drones: int = 1
        self.connections: list['Connection'] = []
        self.garage: list['Drone'] = []


class NormalZone(Zone):
    def __init__(self, designation: str, name: str, x: int, y: int):
        super().__init__(designation, name, x, y)
        self.zone_type: str = "normal"


class RestrictedZone(Zone):
    def __init__(self, designation: str, name: str, x: int, y: int):
        super().__init__(designation, name, x, y)
        self.zone_type: str = "restricted"
        self.cost: int = 2


class PriorityZone(Zone):
    def __init__(self, designation: str, name: str, x: int, y: int):
        super().__init__(designation, name, x, y)
        self.zone_type: str = "priority"
        self.prior = True


class BlockedZone(Zone):
    def __init__(self, designation: str, name: str, x: int, y: int):
        super().__init__(designation, name, x, y)
        self.zone_type: str = "blocked"
        self.cost: int = 0
        self.max_drones: int = 0


class Connection():
    def __init__(self, zone_a: Zone = None, zone_b: Zone = None):
        self.designation: str = "connection"
        self.cost: int = 1
        self.max_link_capacity: int = 1
        self.zone_a = zone_a
        self.zone_b = zone_b


@dataclass
class GameMap:
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zone_dict: dict[str, Zone]
    connections: list[Connection]


class Drone:
    def __init__(self):
        self.name: str = "Drone"
