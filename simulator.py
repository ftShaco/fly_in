from models import GameMap, Drone, Zone


class TurnSimulator:
    def __init__(self, game_map: GameMap) -> None:
        self.turn_count = 0
        self.game_map = game_map
        self.drones_dict: dict[str, Drone] = {}

    def init_first_turn(self) -> None:
        for i in range(self.game_map.nb_drones):
            new_drone = Drone(f"{i}")
            self.game_map.start_hub.garage.append(new_drone)
            self.drones_dict[new_drone.full_tag] = new_drone
        for d in self.drones_dict.values():
            d.current_zone = self.game_map.start_hub

    def execute_turn(self, moves: list[str]) -> None:
        # Transit management
        for d in self.drones_dict.values():
            if d.transit_timer > 0:
                d.transit_timer -= 1
                if d.transit_timer == 0:
                    d.current_zone = d.target_zone
                    d.target_zone.garage.append(d)

        drones_leaving_zone = {}
        drones_entering_zone = {}
        connection_usage = {}
        valid_moves: list[tuple[Zone, Drone]] = []

        # Validating orders
        for m in moves:
            if m == "":
                continue
            d, zone = m.split('-')
            drone = self.drones_dict[d]
            current_zone = drone.current_zone
            destination = self.game_map.zone_dict[zone]
            if drone.transit_timer > 0:
                raise ValueError("Impossible move, drone in transit:\n"
                                 f"drone = {drone}\n "
                                 f"current_zone = {current_zone}\n"
                                 f"destination = {destination}")

            neighbors_list = current_zone.find_neighbors()
            if destination not in neighbors_list:
                raise ValueError("Destination can't be reached\n"
                                 f"drone = {drone}\n "
                                 f"current_zone = {current_zone}\n"
                                 f"destination = {destination}")

            chosen_connection =\
                self.game_map.get_connection(current_zone, destination)
            connection_usage[chosen_connection] = \
                connection_usage.get(chosen_connection, 0) + 1
            if connection_usage[chosen_connection] >\
                    chosen_connection.max_link_capacity:
                raise ValueError("Max link capacity reached, forbidden move"
                                 f"drone = {drone}\n"
                                 f"connection = {chosen_connection}")

            drones_leaving_zone[current_zone] =\
                drones_leaving_zone.get(current_zone, 0) + 1
            if destination.zone_type != "restricted":
                drones_entering_zone[destination] =\
                    drones_entering_zone.get(destination, 0) + 1

            valid_moves.append((destination, drone))

        # Validating next moves
        for destination, entering_nb in drones_entering_zone.items():
            if destination == self.game_map.start_hub or\
                    destination == self.game_map.end_hub:
                continue
            leaving_nb = drones_leaving_zone.get(destination, 0)
            total_futur = len(destination.garage) + entering_nb\
                - leaving_nb
            if total_futur > destination.max_drones:
                raise ValueError("Destination garage already full, "
                                 "forbidden move.\n"
                                 f"drone = {drone}\n"
                                 f"destination = {destination}")

        # Executing valid moves
        for m in valid_moves:
            destination, drone = m
            drone.current_zone.garage.remove(drone)
            drone.current_zone = destination
            if destination.zone_type == "restricted":
                drone.transit_timer = 1
                drone.target_zone = destination
            else:
                destination.garage.append(drone)

        self.turn_count += 1
