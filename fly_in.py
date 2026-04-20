#!/usr/bin/env python3

import sys
from parser import parse_map
from simulator import TurnSimulator
from solver import MapSolver


def main() -> None:
    try:
        config_file = sys.argv[1]
    except Exception as e:
        print(f"{e}\n"
              "Error with the map file, usage: 'p fly_in.py <map_config.txt>'")
        sys.exit(1)

    game_map = parse_map(config_file)
    simulator = TurnSimulator(game_map)
    solver = MapSolver(game_map)
    orders = solver.output_orders()

    simulator.init_first_turn()
    simulator.execute_turn(orders)


if __name__ == "__main__":
    main()
