from models import GameMap, Zone, Connection
import sys


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
            if distances[current] == float('inf'):
                print("Unsolvable map, exiting program.")
                sys.exit(1)
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

    def spatial_temp_dijkstra(self, zone_r: dict[tuple[Zone, int], int],
                              route_r: dict[tuple[Connection, int], int])\
            -> list[Zone]:
        start = self.g_map.start_hub
        end = self.g_map.end_hub
        start_state = (start, 0)
        distances = {start_state: 0}
        my_thumb = {}
        open_set = [start_state]

        while open_set:
            curr_state = min(open_set, key=lambda state: distances[state])
            curr_zone, curr_turn = curr_state

            if curr_turn > 100:
                open_set.remove(curr_state)
                continue

            if curr_zone == end:
                break

            open_set.remove(curr_state)

            possible_moves = curr_zone.find_neighbors() + [curr_zone]
            for next_zone in possible_moves:
                if next_zone == curr_zone:
                    next_turn = curr_turn + 1
                elif next_zone.zone_type == "restricted":
                    next_turn = curr_turn + 2
                else:
                    next_turn = curr_turn + 1

                next_state = (next_zone, next_turn)
                new_cost = distances[curr_state] + (next_turn - curr_turn)

                if next_zone != start and next_zone != end:
                    occupants = zone_r.get(next_state, 0)
                    if occupants >= next_zone.max_drones:
                        continue

                if next_zone != curr_zone:
                    used_route =\
                        self.g_map.get_connection(curr_zone, next_zone)
                    trafic = route_r.get((used_route, curr_turn), 0)
                    if trafic >= used_route.max_link_capacity:
                        continue

                if next_state not in distances or\
                        new_cost < distances[next_state]:
                    distances[next_state] = new_cost
                    my_thumb[next_state] = curr_state
                    if next_state not in open_set:
                        open_set.append(next_state)

        if curr_zone != end:
            return []

        path_states = [curr_state]
        while curr_state != start_state:
            curr_state = my_thumb[curr_state]
            path_states.append(curr_state)
        path_states = path_states[::-1]

        final_path = [state[0] for state in path_states]

        return final_path

    def apply_dijsktra(self) -> list[list[str]]:

        zone_reservations: dict[tuple[Zone, int], int] = {}
        route_reservations: dict[tuple[Connection, int], int] = {}
        all_orders: list[list[str]] = []

        for i in range(self.g_map.nb_drones):
            drone_tag = f"D{i}"
            path = self.spatial_temp_dijkstra(zone_reservations,
                                              route_reservations)
            if not path:
                print(f"No possible path for {drone_tag}, exiting program")
                sys.exit(1)

            self.book_path(path, zone_reservations,
                           route_reservations, all_orders, drone_tag)

        return all_orders

    def book_path(self, path: list[Zone],
                  zone_res: dict[tuple[Zone, int], int],
                  route_res: dict[tuple[Connection, int], int],
                  all_orders: list[list[str]],
                  drone_tag: str) -> None:

        current_turn = 0
        for i in range(len(path)):
            current_zone = path[i]
            zone_res[(current_zone, current_turn)] =\
                zone_res.get((current_zone, current_turn), 0) + 1

            if i < len(path) - 1:
                next_zone = path[i + 1]

                if current_zone == next_zone:
                    current_turn += 1
                else:
                    while len(all_orders) <= current_turn:
                        all_orders.append([])
                    all_orders[current_turn].append(f"{drone_tag}-{next_zone.name}")

                    used_connection =\
                        self.g_map.get_connection(current_zone, next_zone)
                    if used_connection:
                        route_res[(used_connection, current_turn)] =\
                            route_res.get((used_connection, current_turn), 0)+1

                    if next_zone.zone_type == "restricted":
                        current_turn += 2
                    else:
                        current_turn += 1
