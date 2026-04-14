import sys
from parser import parse_map

try:
    config_file = sys.argv[1]
except Exception as e:
    print(f"{e}\n"
          "Error with the map file, usage: 'p fly_in.py <map_config.txt>'")
    sys.exit(1)

game_map = parse_map(config_file)


