from models import GameMap, NormalZone, Connection, Zone
from models import PriorityZone, BlockedZone, RestrictedZone
import sys


def parse_map(config_file: str) -> GameMap:
    """Parse a map configuration file and create a GameMap object.

    Reads a map file with the following format:
    - nb_drones: <number> (must be first line)
    - start_hub: <name> <x> <y> [metadata]
    - end_hub: <name> <x> <y> [metadata]
    - hub: <name> <x> <y> [metadata]
    - connection: <name1>-<name2> [metadata]

    Metadata options: [color=<value>] [zone=<type>] [max_drones=<number>]
                     [max_link_capacity=<number>]

    Args:
        config_file: Path to the map configuration file.

    Returns:
        A fully initialized GameMap object.

    Raises:
        ValueError: If the map file is corrupted or missing required elements.
    """
    new_map = GameMap(nb_drones=0, start_hub=NormalZone('', '', 0, 0),
                      end_hub=NormalZone('', '', 0, 0),
                      zone_dict={}, connections=[])
    try:
        with open(config_file, 'r') as f:
            line_count = 0
            seen_connections = set()
            new_zone: Zone
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                line_count += 1

                parts = line.split('[')
                base_part = parts[0].split()
                if len(parts) > 5:
                    raise ValueError(f"Corrupted map file: {parts}."
                                     "Usage:\n'nb_drones: <number>'\n"
                                     "start_hub: <name> <x> <y> [metadata]\n"
                                     "end_hub: <name> <x> <y> [metadata]\n"
                                     "hub: <name> <x> <y> [metadata]\n"
                                     "connection: <name1>-<name2> [metadata]")
                metadata: dict[str, str] = {}
                possible_keys = ['color', 'zone', 'max_drones',
                                 'max_link_capacity']
                if len(parts) > 1:
                    meta_part = parts[1].strip('[]').split()
                    for i in range(len(meta_part)):
                        split_test = meta_part[i].split('=')
                        if len(split_test) != 2:
                            raise ValueError(f"Corrupted map file: {meta_part}"
                                             " can't be treated")
                        key, value = split_test
                        if value == "":
                            raise ValueError("Corrupted map file: syntax error"
                                             f" near '{key}='. No spaces "
                                             "allowed around '=' in metadata.")
                        if key not in possible_keys:
                            raise ValueError(f"Corrupted map file, {key} "
                                             "isn't an available metadata")
                        if key in metadata.keys():
                            raise ValueError(f"{key} already used, map file "
                                             "considered as corrupted")
                        if key == "max_drones" and not value.isdigit():
                            raise ValueError(f"Corrupted map file: {key}"
                                             " has to be a positive value")
                        metadata[key] = value
                    if not metadata:
                        raise ValueError("No valid values in the metadata part"
                                         ", please fill it or remove it")

                if ':' not in base_part[0]:
                    raise ValueError("Corrupted map file, invalid syntax.\n"
                                     "Usage:\nnb_drones: <number>\n"
                                     "start_hub: <name> <x> <y> [metadata]\n"
                                     "end_hub: <name> <x> <y> [metadata]\n"
                                     "hub: <name> <x> <y> [metadata]\n"
                                     "connection: <name1>-<name2> [metadata]")
                keyword = base_part[0].strip(':')
                possible_keywords = ['nb_drones', 'start_hub', 'end_hub',
                                     'hub', 'connection']
                if keyword not in possible_keywords:
                    raise ValueError(f"Corrupted map file, {keyword} isn't"
                                     " a valid variable")
                if keyword in ['start_hub', 'end_hub', 'hub']:
                    if len(base_part) != 4:
                        raise ValueError(f"Corrupted map file: {base_part}."
                                         "Usage:\n"
                                         "start_hub: <name> <x> <y> [metadata]"
                                         "\nend_hub: <name> <x> <y> [metadata]"
                                         "\nhub: <name> <x> <y> [metadata]")
                    if not base_part[2].lstrip('-').isdigit() or \
                            not base_part[3].lstrip('-').isdigit():
                        raise ValueError("Corrupted map file, coordinates X "
                                         "and Y must be positive integers")

                if keyword == "nb_drones":
                    if line_count != 1:
                        raise ValueError("The first line must define the "
                                         "number of drones using nb_drones:"
                                         "<positive_integer>.")
                    if len(base_part) != 2:
                        raise ValueError(f"Corrupted map file, {base_part}."
                                         "\nUsage: 'nb_drones: <number>' ")
                    new_map.nb_drones = int(base_part[1])
                    if new_map.nb_drones < 1:
                        raise ValueError("Drone number need to be a positive "
                                         f"value: {base_part}")

                elif keyword == "start_hub":
                    if new_map.start_hub.name != "":
                        raise ValueError("Corrupted map file: there can be"
                                         "only one start_hub")
                    new_zone = NormalZone(keyword, base_part[1],
                                          int(base_part[2]), int(base_part[3]))
                    for k, v in metadata.items():
                        if k == "color":
                            new_zone.color = v
                        elif k == "max_drones":
                            new_zone.max_drones = int(v)
                            if new_zone.max_drones < new_map.nb_drones:
                                raise ValueError("Can't load this map, "
                                                 "start_hub need more space "
                                                 "for drones")

                    if new_zone.name in new_map.zone_dict.keys():
                        raise ValueError("Each zone must have a unique name")
                    if new_zone.name.find('-') != -1:
                        raise ValueError("Zone names can use any valid "
                                         "characters but dashes and spaces.")
                    new_map.start_hub = new_zone
                    new_zone.max_drones = new_map.nb_drones
                    new_map.zone_dict[new_zone.name] = new_zone

                elif keyword == "end_hub":
                    if new_map.end_hub.name != "":
                        raise ValueError("Corrupted map file: there can be"
                                         "only one end_hub")
                    new_zone = NormalZone(keyword, base_part[1],
                                          int(base_part[2]), int(base_part[3]))
                    for k, v in metadata.items():
                        if k == "color":
                            new_zone.color = v
                        elif k == "max_drones":
                            new_zone.max_drones = int(v)
                            if new_zone.max_drones < new_map.nb_drones:
                                raise ValueError("Can't load this map, end_hub"
                                                 " need more space for drones")

                    if new_zone.name in new_map.zone_dict.keys():
                        raise ValueError("Each zone must have a unique name")
                    if new_zone.name.find('-') != -1:
                        raise ValueError("Zone names can use any valid "
                                         "characters but dashes and spaces.")
                    new_map.end_hub = new_zone
                    new_zone.max_drones = new_map.nb_drones
                    new_map.zone_dict[new_zone.name] = new_zone

                elif keyword == "hub":
                    possible_zones = ['normal', 'restricted',
                                      'priority', 'blocked']
                    zone_type = metadata.get('zone', 'normal')
                    if zone_type not in possible_zones:
                        raise ValueError(f"Corrupted map file: {zone_type}"
                                         "isn't valid. Available zone types:"
                                         f"{possible_zones}")
                    if zone_type == "normal":
                        new_zone = NormalZone(keyword, base_part[1],
                                              int(base_part[2]),
                                              int(base_part[3]))
                    elif zone_type == "restricted":
                        new_zone = RestrictedZone(keyword, base_part[1],
                                                  int(base_part[2]),
                                                  int(base_part[3]))
                    elif zone_type == "priority":
                        new_zone = PriorityZone(keyword, base_part[1],
                                                int(base_part[2]),
                                                int(base_part[3]))
                    elif zone_type == "blocked":
                        new_zone = BlockedZone(keyword, base_part[1],
                                               int(base_part[2]),
                                               int(base_part[3]))
                    for k, v in metadata.items():
                        if k == "color":
                            new_zone.color = v
                        elif k == "max_drones":
                            new_zone.max_drones = int(v)
                    if new_zone.name in new_map.zone_dict.keys():
                        raise ValueError("Each zone must have a unique name")
                    if new_zone.name.find('-') != -1:
                        raise ValueError("Zone names can use any valid "
                                         "characters but dashes and spaces.")
                    new_map.zone_dict[new_zone.name] = new_zone

                elif keyword == "connection":
                    if base_part[1].count('-') != 1:
                        raise ValueError(f"Corrupted map file: {base_part[1]}"
                                         ", usage = connection: "
                                         "<nameA>-<nameB> [metadata]")
                    a_name, b_name = base_part[1].split('-')
                    if a_name not in new_map.zone_dict or \
                            b_name not in new_map.zone_dict:
                        raise ValueError(f"Corrupted map file: {a_name} or "
                                         f"{b_name} does not exist. Please "
                                         "initialize hubs before connections"
                                         ", and make sure names are correctly"
                                         " written")

                    route_id = tuple(sorted([a_name, b_name]))
                    if route_id in seen_connections:
                        raise ValueError(f"Corrupted map file: {base_part[1]}"
                                         "\nConnection already exists. ")
                    seen_connections.add(route_id)

                    a_zone = new_map.zone_dict[a_name]
                    b_zone = new_map.zone_dict[b_name]
                    new_connec = Connection(a_zone, b_zone)
                    if 'max_link_capacity' in metadata:
                        if not metadata['max_link_capacity'].isdigit():
                            raise ValueError("Corrupted map file: "
                                             "max_link_capacity must be a "
                                             "positive integer")
                        new_connec.max_link_capacity = \
                            int(metadata['max_link_capacity'])

                    new_map.connections.append(new_connec)
                    a_zone.connections.append(new_connec)
                    b_zone.connections.append(new_connec)

        if not new_map.start_hub or not new_map.end_hub or not \
            new_map.connections\
                or not new_map.zone_dict:
            raise ValueError("Corrupted map file. "
                             "Please make sure there are :\n"
                             "- start_hub\n- end_hub\n- hubs\n- connections")
        if new_map.start_hub.x == new_map.end_hub.x and \
                new_map.start_hub.y == new_map.end_hub.y:
            raise ValueError("Corrupted map file, start_hub and "
                             "end_hub cannot "
                             "share the same coordinates")
        if not new_map.start_hub.connections or not \
                new_map.end_hub.connections:
            raise ValueError("Corrupted map file: impossible to resolve")

    except Exception as e:
        print(f"Error occured while loading the map.\n{e}")
        print("\nExiting program...")
        sys.exit(1)

    return new_map
