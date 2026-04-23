import sys
import argparse
from parser import parse_map
from simulator import TurnSimulator
from solver import MapSolver
from visualizer import Displayer
from models import Analyst


def main() -> None:
    parser = argparse.ArgumentParser(description="Drone Swarm"
                                     "Pathfinding Simulator")
    parser.add_argument("map_file",
                        help="Path to the map configuration file (.txt)")
    parser.add_argument("--visual", action="store_true",
                        help="Launch the Pygame visualizer")
    parser.add_argument("--analysis", action="store_true",
                        help="Print performance metrics")

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)

    config_file = args.map_file

    try:
        game_map = parse_map(config_file)
        simulator = TurnSimulator(game_map)
        solver = MapSolver(game_map)

        simulator.init_first_turn()
        all_orders = solver.apply_dijsktra()

        for order in all_orders:
            simulator.execute_turn(order)

        with open('output.txt', 'w') as file:
            for order in all_orders:
                if order:
                    new_line = " ".join(order)
                    file.write(f"{new_line}\n")
                else:
                    file.write("\n")

        print(f"\nSimulated in {simulator.turn_count} turn(s)\n")
        print("Simulation output available in 'output.txt'\n")

        if args.analysis:
            evaluator = Analyst(all_orders, game_map)
            analysis = evaluator.evaluate_performance()
            print("\n=== ANALYSIS ===")
            print(f"Efficiency: {analysis['efficiency']:.1f}%")
            print(f"Avg turns/drone: {analysis['flowtime']:.1f}")
            print(f"Total path cost: {analysis['total_cost']}")

        if args.visual:
            visualizer = Displayer(game_map, "output.txt")
            visualizer.display()

        if not args.visual:
            print("Visual available with flag --visual\n"
                  f"Run : 'make run MAP={args.map_file} FLAGS=--visual'\n")

        if not args.analysis:
            print("Analysis available with flag --analysis\n"
                  f"Run : 'make run MAP={args.map_file} FLAGS=--analysis'\n")

    except Exception as e:
        print(f"Error occured:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
