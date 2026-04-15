#!/usr/bin/env python3

import sys
from parser import parse_map


def main():
    try:
        config_file = sys.argv[1]
    except Exception as e:
        print(f"{e}\n"
              "Error with the map file, usage: 'p fly_in.py <map_config.txt>'")
        sys.exit(1)

    game_map = parse_map(config_file)


if __name__ == "__main__":
    main()
