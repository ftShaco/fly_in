*This project has been created as part of the 42 curriculum by jreibel

# Drone Swarm Cooperative Pathfinding

## Description
This project implements a Multi-Agent Pathfinding (MAPF) engine and a 2D visualizer for a drone routing simulation. The primary goal is to navigate a fleet of drones from a starting hub to an ending hub across a complex network of zones and connections, while strictly minimizing the total number of turns. 

The environment is highly constrained:
* **Zone Capacities:** Hubs can only hold a limited number of drones simultaneously.
* **Link Capacities:** Connections between zones have traffic limits.
* **Zone Types:** Different zones have distinct traversal costs (e.g., Restricted zones take 2 turns and hold drones in transit).

The project is divided into distinct, decoupled modules: a robust map parser, a strict physical simulator (The Referee), an advanced spatio-temporal solver (The Brain), and a Pygame-based GUI (The Visualizer).

---

## Instructions

### Prerequisites
* Python 3.10 or higher (relies on modern type hinting)
* `pygame` library for the visualizer

### Installation
Clone the repository and install the required dependencies:
```bash
git clone <your_repository_url>
cd <repository_directory>
pip install pygame



Execution

1. Run the Simulation (Solver + Referee)
To calculate the optimal paths and generate the output.txt file containing the orders for each turn:

python main.py maps/challenger/01_the_impossible_dream.txt

2. Run the Visualizer
To watch the simulation playback:
Bash

python visualizer.py maps/challenger/01_the_impossible_dream.txt output.txt

Visualizer Controls:

    SPACE: Play / Pause the simulation.

    RIGHT ARROW: Step forward by one turn.

    LEFT ARROW: Step backward by one turn.

    ESC: Quit the visualizer.

Algorithm Choices & Implementation Strategy

To solve this highly constrained MAPF problem, a standard 2D pathfinding algorithm (like A* or Dijkstra) is insufficient, as it cannot account for dynamic obstacles (other drones) and network capacities over time.
Cooperative Spatio-Temporal Pathfinding

The core algorithm is based on Prioritized Planning combined with a Spatio-Temporal Dijkstra.

    The 3D Space-Time Graph:
    Instead of searching for a path through physical Zones, the algorithm searches through States defined as (Zone, Turn). This introduces the 4th dimension (Time) into the graph.

    Global Reservation Tables:
    As each drone sequentially calculates its optimal path, it "books" its presence in a global agenda (zone_reservations and route_reservations).

    Dynamic Avoidance:
    When subsequent drones calculate their paths, they query the reservation tables. If a zone or a route has reached its max_drones or max_link_capacity at a specific Turn, that edge is considered temporarily blocked.

    Waiting in Place:
    The algorithm allows a node to be a neighbor to itself (current_zone, current_turn + 1). This allows drones to deliberately wait in a safe hub to let traffic clear before proceeding, completely preventing deadlocks in severe bottlenecks.

Visual Representation

The visualizer is built using Pygame and strictly follows the Model-View separation principle. It acts purely as a timeline player, reading the initial map and the generated output.txt without computing any game logic.
Enhancing User Experience (UX)

    Smooth Animation (Linear Interpolation): Drones do not simply teleport from node to node. The visualizer parses the timeline and uses linear interpolation (Lerp) to smoothly animate drones traversing the connections between turns, making traffic flow clearly legible.

    Color-Coded Topology: Zones are visually distinguished by type to help the user understand the algorithmic decisions (e.g., Restricted zones in red, Priority zones in gold).

    Interactive Playback: The ability to pause and manually step through the timeline (frame by frame) allows users to audit specific bottlenecks and appreciate how the algorithm resolves complex collision scenarios in real-time.

Resources
Classic References

    Cooperative Pathfinding (David Silver, 2005) - Fundamental concepts on Prioritized Planning and reservation tables in A*.

    Multi-Agent Path Finding (MAPF) literature - Concepts of space-time A* and conflict resolution.

Artificial Intelligence Usage

AI (Google Gemini) was used as an interactive mentor and pair-programmer throughout the development of this project. Specifically, AI assisted with:

    Architecture Design: Helping to separate the project into distinct responsibilities (Parser, Simulator, Solver) avoiding tight coupling.

    Algorithm Structuring: Transitioning from a theoretical 2D Dijkstra to a Spatio-Temporal Dijkstra by introducing the concept of (Zone, Turn) tuples and reservation dictionaries.

    Debugging Python Specifics: Identifying tricky Python behaviors such as dictionary mutations, list append returns, and generator expressions.

    Pygame Boilerplate: Providing the initial rendering loop and Lerp (Linear Interpolation) math to animate the drones smoothly between states.