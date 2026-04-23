from dataclasses import dataclass
from abc import ABC
from typing import Optional, Self


class Zone(ABC):
    """Abstract base class representing a zone in the game map.

    A zone is a location on the map where drones can be stationed or
    pass through. Each zone has properties like position, type, capacity,
    and connections to other zones.

    Attributes:
        name: The unique identifier for the zone.
        x: X coordinate of the zone on the map.
        y: Y coordinate of the zone on the map.
        zone_type: The type of zone (e.g., 'normal', 'restricted', 'priority').
        designation: The category or designation of the zone.
        color: Optional color value for visualization.
        prior: Whether the zone has priority status.
        cost: Movement cost associated with traversing this zone.
        max_drones: Maximum number of drones that can occupy the zone.
        connections: List of connections linking to other zones.
        garage: List of drones currently stationed in this zone.
    """

    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        """Initialize a Zone.

        Args:
            designation: The category or designation of the zone.
            name: The unique identifier for the zone.
            x: X coordinate of the zone on the map.
            y: Y coordinate of the zone on the map.
        """
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
        """Find all accessible neighboring zones.

        Returns a list of zones that are directly connected to this zone and
        are not blocked zones.

        Returns:
            A list of accessible neighboring Zone objects.
        """
        valid_neighbors = []
        for c in self.connections:
            opposite_zone = c.get_opposite_zone(self)
            if not opposite_zone.zone_type == "blocked":
                valid_neighbors.append(opposite_zone)
        return valid_neighbors


class NormalZone(Zone):
    """A standard zone with no special properties."""

    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        """Initialize a NormalZone.

        Args:
            designation: The category or designation of the zone.
            name: The unique identifier for the zone.
            x: X coordinate of the zone on the map.
            y: Y coordinate of the zone on the map.
        """
        super().__init__(designation, name, x, y)
        self.zone_type: str = "normal"


class RestrictedZone(Zone):
    """A zone with restricted access that takes longer to traverse.

    Drones entering restricted zones require extra transit time.
    """

    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        """Initialize a RestrictedZone.

        Args:
            designation: The category or designation of the zone.
            name: The unique identifier for the zone.
            x: X coordinate of the zone on the map.
            y: Y coordinate of the zone on the map.
        """
        super().__init__(designation, name, x, y)
        self.zone_type: str = "restricted"
        self.cost: int = 2


class PriorityZone(Zone):
    """A zone with priority status for faster drone processing."""

    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        """Initialize a PriorityZone.

        Args:
            designation: The category or designation of the zone.
            name: The unique identifier for the zone.
            x: X coordinate of the zone on the map.
            y: Y coordinate of the zone on the map.
        """
        super().__init__(designation, name, x, y)
        self.zone_type: str = "priority"
        self.prior = True


class BlockedZone(Zone):
    """A zone that is blocked and cannot be traversed or occupied by drones."""

    def __init__(self: Self, designation: str, name: str, x: int, y: int)\
            -> None:
        """Initialize a BlockedZone.

        Args:
            designation: The category or designation of the zone.
            name: The unique identifier for the zone.
            x: X coordinate of the zone on the map.
            y: Y coordinate of the zone on the map.
        """
        super().__init__(designation, name, x, y)
        self.zone_type: str = "blocked"
        self.cost: int = 0
        self.max_drones: int = 0


class Connection():
    """Represents a link between two zones.

    A connection enables drones to move from one zone to another and has
    properties like cost and maximum link capacity.

    Attributes:
        designation: Type identifier for the connection.
        cost: Movement cost to traverse the connection.
        max_link_capacity: Maximum number of drones that can use the connection
            simultaneously.
        zone_a: First zone in the connection pair.
        zone_b: Second zone in the connection pair.
    """

    def __init__(self: Self, zone_a: Zone, zone_b: Zone) -> None:
        """Initialize a Connection between two zones.

        Args:
            zone_a: The first zone to connect.
            zone_b: The second zone to connect.
        """
        self.designation: str = "connection"
        self.cost: int = 1
        self.max_link_capacity: int = 1
        self.zone_a = zone_a
        self.zone_b = zone_b

    def get_opposite_zone(self: Self, curr_zone: Zone) -> Zone:
        """Get the zone on the opposite end of the connection.

        Args:
            curr_zone: The current zone in the connection.

        Returns:
            The zone on the opposite end of the connection.
        """
        return self.zone_b if curr_zone == self.zone_a else self.zone_a


@dataclass
class GameMap:
    """The game map containing all zones, connections, and drones.

    This dataclass represents the complete game environment with zones,
    connections between them, and parameters for drone management.

    Attributes:
        nb_drones: The total number of drones in the game.
        start_hub: The starting zone where drones begin.
        end_hub: The destination zone where drones must reach.
        zone_dict: Dictionary mapping zone names to Zone objects.
        connections: List of all connections between zones.
    """

    nb_drones: int
    start_hub: Zone
    end_hub: Zone
    zone_dict: dict[str, Zone]
    connections: list[Connection]

    def get_connection(self: Self, zone_a: Zone, zone_b: Zone)\
            -> Connection | None:
        """Get the connection between two zones.

        Args:
            zone_a: The first zone.
            zone_b: The second zone.

        Returns:
            The Connection object linking the two zones, or None if no direct
            connection exists.
        """
        for c in zone_a.connections:
            if c.get_opposite_zone(zone_a) == zone_b:
                return c
        return None


class Drone:
    """Represents a drone in the simulation.

    A drone is an entity that moves through the game map from the start hub
    to the end hub, following a calculated path.

    Attributes:
        name: The name prefix for the drone (default: "D").
        id: The unique identifier for the drone.
        full_tag: The complete tag combining name and ID (e.g., "D0").
        current_zone: The zone where the drone is currently located.
        target_zone: The zone the drone is moving towards.
        transit_timer: Counter for tracking transit time in restricted zones.
    """

    def __init__(self: Self, id: str) -> None:
        """Initialize a Drone.

        Args:
            id: The unique identifier for the drone.
        """
        self.name = "D"
        self.id = id
        self.full_tag: str = f"{self.name}{self.id}"
        self.current_zone: Zone
        self.target_zone: Zone
        self.transit_timer: int = 0


class Analyst:
    def __init__(self: Self, orders: list[list[str]],
                 game_map: GameMap) -> None:
        self.game_map = game_map
        self.orders = orders
        self.drone_nb = game_map.nb_drones
        self.end_hub_name = game_map.end_hub.name

    def calculate_efficiency(self: Self) -> float:
        efficiency = 0
        turns = 0
        for order in self.orders:
            turns += 1
            total_order = len(order)
            efficiency += (total_order / self.drone_nb * 100)
        efficiency /= turns

        return efficiency

    def calculate_flowtime(self: Self) -> float:
        flowtime = 0
        i = 0
        for order in self.orders:
            i += 1
            for s in order:
                if s.split('-')[1] == self.end_hub_name:
                    flowtime += i

        avg_flowtime = flowtime / self.drone_nb
        return avg_flowtime

    def calculate_path_cost(self: Self) -> float:
        total_cost = 0
        for order in self.orders:
            for o in order:
                destination = o.split('-')[1]
                total_cost += self.game_map.zone_dict[destination].cost

        return total_cost

    def evaluate_performance(self: Self) -> dict[str, float]:
        return {
            "efficiency": self.calculate_efficiency(),
            "flowtime": self.calculate_flowtime(),
            "total_cost": self.calculate_path_cost()
        }
