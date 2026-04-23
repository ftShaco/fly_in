from typing import Self
from models import GameMap
import sys
import pygame


WIDTH, HEIGHT = 2560, 1440
FPS = 60
SCALE = 80
OFFSET_X, OFFSET_Y = WIDTH // 6, HEIGHT // 2

COLORS = {
    "bg": (30, 30, 30),
    "line": (100, 100, 100),

    "green": (50, 200, 50),     # Start/End
    "blue": (50, 150, 255),     # Normal paths
    "yellow": (255, 255, 0),    # Junction/merge
    "orange": (255, 165, 0),    # Bottlenecks/gates
    "red": (220, 50, 50),       # Dead ends/traps
    "purple": (150, 50, 200),   # Restricted zones
    "cyan": (50, 220, 220),     # Priority zones

    "brown": (139, 69, 19),
    "maroon": (128, 0, 0),
    "gold": (255, 215, 0),
    "darkred": (139, 0, 0),
    "violet": (238, 130, 238),
    "crimson": (220, 20, 60),
    "rainbow": (255, 105, 180),
    "black": (0, 0, 0),

    "unknown": (150, 150, 150)
}


class Displayer:
    """Handles visualization of the game map and drone movement simulation.

    This class uses Pygame to render the map with zones and connections,
    and animate drone movements across the map based on a timeline of moves.

    Attributes:
        game_map: The GameMap to display.
        output: Path to the file containing movement orders/timeline.
    """

    def __init__(self: Self, game_map: GameMap, output: str) -> None:
        """Initialize the Displayer.

        Args:
            game_map: The GameMap to display.
            output: Path to the file containing movement orders for animation.
        """
        self.game_map = game_map
        self.output = output

    def world_to_screen(self: Self, x: float, y: float) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates.

        Args:
            x: World X coordinate.
            y: World Y coordinate.

        Returns:
            A tuple (screen_x, screen_y) with pixel coordinates for rendering.
        """
        screen_x = int(OFFSET_X + (x * SCALE))
        screen_y = int(OFFSET_Y - (y * SCALE))
        return screen_x, screen_y

    def load_timeline(self: Self, output_file: str, game_map: GameMap)\
            -> list[dict[str, str]]:
        """Load drone movement timeline from output file.

        Reads movement orders and constructs a timeline showing drone positions
        at each turn. Each turn lists which zone each drone is in.

        Args:
            output_file: Path to the file containing movement orders.
            game_map: The GameMap with drone and zone information.

        Returns:
            A list of dictionaries where each dictionary maps drone tags to
            their zone names for that turn.

        Raises:
            SystemExit: If the output file cannot be found.
        """
        timeline = []
        current_state = {}
        for i in range(game_map.nb_drones):
            current_state[f"D{i}"] = game_map.start_hub.name
        timeline.append(current_state.copy())

        try:
            with open(output_file, 'r') as f:
                for line in f:
                    moves = line.strip().split()

                    for move in moves:
                        drone, dest = move.split('-')
                        current_state[drone] = dest

                    timeline.append(current_state.copy())
        except FileNotFoundError:
            print(f"Erreur : Impossible de trouver le fichier {output_file}")
            sys.exit(1)

        return timeline

    def draw_map(self: Self, screen: pygame.Surface,
                 game_map: GameMap) -> None:
        """Draw the map including zones and connections on the screen.

        Renders all zones as circles with appropriate colors based on
        their type, and connections as lines between them.

        Args:
            screen: The pygame Surface to draw on.
            game_map: The GameMap containing zones and connections to render.
        """
        screen.fill(COLORS["bg"])

        for con in game_map.connections:
            x1, y1 = self.world_to_screen(con.zone_a.x, con.zone_a.y)
            x2, y2 = self.world_to_screen(con.zone_b.x, con.zone_b.y)
            pygame.draw.line(screen, COLORS["line"], (x1, y1), (x2, y2), 4)

        for zone in game_map.zone_dict.values():
            x, y = self.world_to_screen(zone.x, zone.y)

            if hasattr(zone, 'color') and zone.color is not None:
                color = COLORS.get(zone.color.lower(), COLORS["unknown"])
            else:
                if zone.zone_type == "restricted":
                    color = COLORS["purple"]
                elif zone.zone_type == "priority":
                    color = COLORS["cyan"]
                else:
                    color = COLORS["blue"]

            if zone == game_map.start_hub or zone == game_map.end_hub:
                color = COLORS["green"]

            pygame.draw.circle(screen, color, (x, y), 15)
            pygame.draw.circle(screen, (200, 200, 200), (x, y), 15, 1)

    def draw_drones(self: Self, screen: pygame.Surface, game_map: GameMap,
                    timeline: list[dict[str, str]], current_turn: int,
                    progress: float) -> None:
        """Draw drones on the screen with smooth animation between zones.

        Interpolates drone positions between their current and next zones
        based on animation progress to create smooth movement animation.

        Args:
            screen: The pygame Surface to draw on.
            game_map: The GameMap containing zone positions.
            timeline: The timeline of drone positions for each turn.
            current_turn: The current turn number in the animation.
            progress: Animation progress from 0.0 to 1.0 for the current turn.
        """

        state_now = timeline[current_turn]

        state_next = timeline[current_turn + 1] if\
            current_turn + 1 < len(timeline) else state_now

        for drone, zone_now_name in state_now.items():
            zone_next_name = state_next[drone]

            zone_now = game_map.zone_dict[zone_now_name]
            zone_next = game_map.zone_dict[zone_next_name]

            x_now, y_now = zone_now.x, zone_now.y
            x_next, y_next = zone_next.x, zone_next.y

            current_x = x_now + (x_next - x_now) * progress
            current_y = y_now + (y_next - y_now) * progress

            screen_x, screen_y = self.world_to_screen(current_x, current_y)

            pygame.draw.circle(screen, (50, 150, 255), (screen_x, screen_y), 8)

            pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y),
                               8, 2)

    def display(self: Self) -> None:
        """Start the interactive animation display of drone movements.

        Initializes pygame and creates an interactive window showing the map
        and animating drone movements based on the loaded timeline. Supports
        play/pause controls and frame-by-frame navigation.
        """

        game_map = self.game_map
        timeline = self.load_timeline(self.output, game_map)
        max_turns = len(timeline) - 1

        pygame.init()
        infoObject = pygame.display.Info()

        global WIDTH, HEIGHT, OFFSET_X, OFFSET_Y
        WIDTH = int(infoObject.current_w * 0.9)
        HEIGHT = int(infoObject.current_h * 0.9)

        OFFSET_X, OFFSET_Y = WIDTH // 6, HEIGHT // 2

        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Drone Simulator - L'Essaim IA")
        clock = pygame.time.Clock()

        current_turn = 0
        anim_progress = 0.0
        anim_speed = 0.05
        is_playing = True

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        is_playing = not is_playing
                    elif event.key == pygame.K_RIGHT:
                        if current_turn < max_turns:
                            current_turn += 1
                            anim_progress = 0.0
                    elif event.key == pygame.K_LEFT:
                        if current_turn > 0:
                            current_turn -= 1
                            anim_progress = 0.0
                    elif event.key == pygame.K_r:
                        current_turn = 0
                        anim_progress = 0.0
                        is_playing = True

            if is_playing and current_turn < max_turns:
                anim_progress += anim_speed
                if anim_progress >= 1.0:
                    anim_progress = 0.0
                    current_turn += 1

            if current_turn == max_turns:
                is_playing = False
                anim_progress = 0.0

            self.draw_map(screen, game_map)
            self.draw_drones(screen, game_map, timeline, current_turn,
                             anim_progress)

            font = pygame.font.SysFont(None, 36)
            header_text = font.render(f"Tour : {current_turn} / {max_turns} "
                                      "| [Espace] Play/Pause [R] Replay", True,
                                      (255, 255, 255))
            screen.blit(header_text, (20, 20))

            legend_font = pygame.font.SysFont(None, 24)

            legend_items = [
                ("Start/End zones", COLORS["green"]),
                ("Normal paths", COLORS["blue"]),
                ("Junction/merge points", COLORS["yellow"]),
                ("Bottlenecks/gates", COLORS["orange"]),
                ("Dead ends/traps", COLORS["red"]),
                ("Restricted zones", COLORS["purple"]),
                ("Priority zones", COLORS["cyan"])
            ]

            title_surf = legend_font.render("Color Coding:", True,
                                            (255, 255, 255))
            screen.blit(title_surf, (20, 60))

            start_y = 90
            for text_str, color in legend_items:
                pygame.draw.circle(screen, color, (35, start_y + 7), 8)
                pygame.draw.circle(screen, (200, 200, 200), (35, start_y + 7),
                                   8, 1)

                text_surf = legend_font.render(text_str, True, (200, 200, 200))
                screen.blit(text_surf, (55, start_y))

                start_y += 25

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
