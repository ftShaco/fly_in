from dataclasses import dataclass
from abc import ABC
from typing import Optional, Self


class Zone(ABC):
    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
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

    def find_neighbors(self: Self) -> list['Zone']:
        valid_neighbors = []
        for c in self.connections:
            opposite_zone = c.get_opposite_zone(self)
            if not opposite_zone.zone_type == "blocked":
                valid_neighbors.append(opposite_zone)
        return valid_neighbors


class NormalZone(Zone):
    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        super().__init__(designation, name, x, y)
        self.zone_type: str = "normal"


class RestrictedZone(Zone):
    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        super().__init__(designation, name, x, y)
        self.zone_type: str = "restricted"
        self.cost: int = 2


class PriorityZone(Zone):
    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        super().__init__(designation, name, x, y)
        self.zone_type: str = "priority"
        self.prior = True


class BlockedZone(Zone):
    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        super().__init__(designation, name, x, y)
        self.zone_type: str = "blocked"
        self.cost: int = 0
        self.max_drones: int = 0


class Connection():
    def __init__(self: Self, zone_a: Zone, zone_b: Zone) -> None:
        self.designation: str = "connection"
        self.cost: int = 1
        self.max_link_capacity: int = 1
        self.zone_a = zone_a
        self.zone_b = zone_b

    def get_opposite_zone(self: Self, curr_zone: Zone) -> Zone:
        return self.zone_b if curr_zone == self.zone_a else self.zone_a


@dataclass
class GameMap:
    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zone_dict: dict[str, Zone]
    connections: list[Connection]

    def get_connection(self: Self, zone_a: Zone, zone_b: Zone)\
            -> Connection:
        for c in zone_a.connections:
            if c.get_opposite_zone(zone_a) == zone_b:
                return c
        return None


class Drone:
    def __init__(self: Self, id: str) -> None:
        self.name = "D"
        self.id = id
        self.full_tag: str = f"{self.name}{self.id}"
        self.current_zone: Zone
        self.target_zone: Zone
        self.transit_timer: int = 0
