from models import GameMap, Zone, BlockedZone
from models import NormalZone, PriorityZone, RestrictedZone


class MapSolver:
    def __init__(self, g_map: GameMap):
        self.g_map = g_map

    def output_orders() -> list[str]:
        pass

    def solve_dijsktra(g_map: GameMap) -> list[Zone]:
        start = g_map.start_hub
        end = g_map.end_hub

        distances = {zone: float('inf') for zone in g_map.zone_dict.values()}
        distances[start] = 0

        my_thumb = {}
        unvisited = list(g_map.zone_dict.values())

        while unvisited:
            current = min(unvisited, key=lambda zone: distances[zone])
            if current == end:
                break
            unvisited.remove(current)
            for n in current.find_neighbors():
                if n.zone_type == "normal" or n.zone_type == "priority":
                    new_cost = distances[current] + 1
                elif n.zone_type == "restricted":
                    new_cost = distances[current] + 2
                if new_cost < distances[n]:
                    distances[n] = new_cost
                    my_thumb[n] = current

        path = [end]
        current = end
        while current != start:
            current = my_thumb[current]
            path.append(current)

        return path[::-1]

    def spatial_temp_dijkstra(self, g_map: GameMap,
                              reservations: dict[tuple[Zone, int], int])\
            -> list[tuple[Zone, str]]:

        start = g_map.start_hub
        end = g_map.end_hub

        distances = {zone: float('inf') for zone in g_map.zone_dict.values()}
        distances[start] = 0

        my_thumb = {}
        unvisited = list(g_map.zone_dict.values())

        while unvisited:


    def apply_dijsktra(self):
        first_path = self.solve_dijsktra(self.g_map)
        spatial_path = self.path_to_spatial_path(first_path)

        zone_reservations: dict[tuple[Zone, int], int] = [spatial_path]
        route_reservations: dict[tuple[Zone, int], int] = []
        for drone in self.g_map.nb_drones:
            path = self.spatial_temp_dijkstra(zone_reservations)

    def path_to_spatial_path(self, path: list[Zone]) -> dict[tuple[Zone, int], int]:
        spatial_path = {}
        current_turn = 0
        for p in path:
            spatial_path[p, current_turn] = 1
            if p.zone_type == "restricted":
                current_turn += 2
            else:
                current_turn += 1
        return spatial_path
