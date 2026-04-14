from models import GameMap, NormalZone, PriorityZone, RestrictedZone, BlockedZone, Zone
import sys


# type, :, nom, coords/metadata, metadata

def parse_map(config_file: str) -> GameMap:
    new_map = GameMap(nb_drones=0, start_hub="", end_hub="", zone_dict={}, connections=[])
    try:
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split('[')
                base_part = parts[0].split()
                metadata = {}
                if len(parts) > 1:
                    meta_part = parts[1].strip('[]').split()
                    for i in range(len(meta_part)):
                        key, value = meta_part[i].split('=')
                        metadata[key] = value

                keyword = base_part[0].strip(':')
                if keyword == "nb_drones":
                    new_map.nb_drones = int(base_part[1])
                elif keyword == "start_hub":
                    start = Zone(sys.maxsize, None)


