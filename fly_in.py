#!/usr/bin/env python3

import sys
from parser import parse_map
from simulator import TurnSimulator
from solver import MapSolver
from visualizer import Displayer


def main() -> None:
    try:
        config_file = sys.argv[1]
    except Exception as e:
        print(f"{e}\n"
              "Error with the map file, usage: 'p fly_in.py <map_config.txt>'")
        sys.exit(1)
    try:
        game_map = parse_map(config_file)
        simulator = TurnSimulator(game_map)
        solver = MapSolver(game_map)

        simulator.init_first_turn()
        all_orders = solver.apply_dijsktra()

        with open('output.txt', 'w') as file:
            for order in all_orders:
                if order:
                    new_line = " ".join(order)
                    file.write(f"{new_line}\n")
                else:
                    file.write("\n")

        for order in all_orders:
            simulator.execute_turn(order)

        visualizer = Displayer(game_map, "output.txt")
        visualizer.display()

        print(f"Simulated in {simulator.turn_count} turn")
    except Exception as e:
        print(f"Error occured:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
