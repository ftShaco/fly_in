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
    """Analyzes and evaluates the performance of drone pathfinding solutions.

    This class calculates various performance metrics for a completed
    simulation including efficiency, flowtime, and path costs.

    Attributes:
        game_map: The GameMap used in the simulation.
        orders: List of turn-by-turn movement orders from the solver.
        drone_nb: The total number of drones in the simulation.
        end_hub_name: The name of the destination zone.
    """

    def __init__(self: Self, orders: list[list[str]],
                 game_map: GameMap) -> None:
        """Initialize the Analyst.

        Args:
            orders: List of movement orders, one list per turn.
            game_map: The GameMap used in the simulation.
        """
        self.game_map = game_map
        self.orders = orders
        self.drone_nb = game_map.nb_drones
        self.end_hub_name = game_map.end_hub.name

    def calculate_efficiency(self: Self) -> float:
        """Calculate the average efficiency of drone usage per turn.

        Efficiency measures the average percentage of drones being utilized
        across all turns (percentage of drones with orders).

        Returns:
            The average efficiency as a percentage (0-100).
        """
        efficiency = 0.0
        turns = 0
        for order in self.orders:
            turns += 1
            total_order = len(order)
            efficiency += (total_order / self.drone_nb * 100)
        efficiency /= turns

        return efficiency

    def calculate_flowtime(self: Self) -> float:
        """Calculate the average flowtime (turns per drone to reach end hub).

        Flowtime measures how many turns on average it takes for a drone to
        reach the destination from start to finish.

        Returns:
            The average flowtime in turns.
        """
        flowtime = 0.0
        i = 0
        for order in self.orders:
            i += 1
            for s in order:
                if s.split('-')[1] == self.end_hub_name:
                    flowtime += i

        avg_flowtime = flowtime / self.drone_nb
        return avg_flowtime

    def calculate_path_cost(self: Self) -> float:
        """Calculate the total movement cost across all drone paths.

        Path cost is the sum of all zone traversal costs for every drone
        as they move from start to end hub.

        Returns:
            The total cost accumulated across all drone movements.
        """
        total_cost = 0
        for order in self.orders:
            for o in order:
                destination = o.split('-')[1]
                total_cost += self.game_map.zone_dict[destination].cost

        return total_cost

    def evaluate_performance(self: Self) -> dict[str, float]:
        """Evaluate all performance metrics for the simulation.

        Computes and returns a comprehensive analysis of the solution quality
        including efficiency, flowtime, and total path cost.

        Returns:
            A dictionary with keys:
                - 'efficiency': Average drone utilization percentage
                - 'flowtime': Average turns per drone
                - 'total_cost': Total zone traversal cost
        """
        return {
            "efficiency": self.calculate_efficiency(),
            "flowtime": self.calculate_flowtime(),
            "total_cost": self.calculate_path_cost()
        }

    def turn_occupacy(self: Self) -> dict[list[str]]:
        route_caps = {}
        for conn in self.game_map.connections:
            route_id = tuple(sorted([conn.zone_a.name, conn.zone_b.name]))
            route_caps[route_id] = getattr(conn, 'max_link_capacity', '∞')

        map_occupacy: dict[int, list[str]] = {}
        map_occupacy[0] = [f"{self.game_map.start_hub.name}: "
                           f"{self.game_map.nb_drones}/"
                           f"{self.game_map.nb_drones}"]
        positions = {f"D{i}": self.game_map.start_hub.name for i
                     in range(self.drone_nb)}

        for turn_idx, turn_orders in enumerate(self.orders, start=1):
            traffic_counts = {route_id: 0 for route_id in route_caps.keys()}
            zone_counts = {zone_name: 0 for zone_name in
                           self.game_map.zone_dict}
            moving_drones = set()

            for move in turn_orders:
                drone, dest = move.split('-')
                origin = positions[drone]

                if origin != dest:
                    moving_drones.add(drone)
                    route_id = tuple(sorted([origin, dest]))
                    if route_id in traffic_counts:
                        traffic_counts[route_id] += 1

                positions[drone] = dest

            for drone, pos in positions.items():
                if drone not in moving_drones:
                    zone_counts[pos] += 1

            zone_parts = []
            for zone_name, count in zone_counts.items():
                if count > 0:
                    max_cap = self.game_map.zone_dict[zone_name].max_drones
                    zone_parts.append(f"{zone_name}: {count}/{max_cap}")

            link_parts = []
            for route_id, count in traffic_counts.items():
                if count > 0:
                    route_name = f"{route_id[0]}-{route_id[1]}"
                    max_cap = route_caps[route_id]
                    link_parts.append(f"{route_name}: {count}/{max_cap}")

            map_occupacy[turn_idx] = zone_parts + link_parts

        map_occupacy[turn_idx + 1] = [f"{self.game_map.end_hub.name}: "
                                      f"{self.game_map.nb_drones}/"
                                      f"{self.game_map.nb_drones}"]

        return map_occupacy
