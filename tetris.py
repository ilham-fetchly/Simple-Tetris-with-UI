import pygame
import random
import sys
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Initialize Pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BACKGROUND_COLOR = (30, 30, 30)

# Define the grid
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_SIZE * GRID_WIDTH + 200
SCREEN_HEIGHT = GRID_SIZE * GRID_HEIGHT

# Define tetromino shapes and their colors
TETROMINOES = {
    "I": {"shape": [[1, 1, 1, 1]], "color": CYAN},
    "O": {"shape": [[1, 1], [1, 1]], "color": YELLOW},
    "S": {"shape": [[1, 1, 0], [0, 1, 1]], "color": GREEN},
    "Z": {"shape": [[0, 1, 1], [1, 1, 0]], "color": RED},
    "J": {"shape": [[1, 0, 0], [1, 1, 1]], "color": BLUE},
    "L": {"shape": [[0, 0, 1], [1, 1, 1]], "color": ORANGE},
    "T": {"shape": [[1, 1, 1], [0, 1, 0]], "color": MAGENTA},
}

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Tetris with UI")
clock = pygame.time.Clock()

# Load fonts once
FONT_SMALL = pygame.font.Font(None, 24)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_LARGE = pygame.font.Font(None, 48)

# Pre-create button rectangles
CONTROL_BUTTONS = {
    "LEFT": pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 50, 160, 40),
    "RIGHT": pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 110, 160, 40),
    "DOWN": pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 170, 160, 40),
    "ROTATE": pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 230, 160, 40),
}

SPEED_BUTTONS = {
    "SLOWER": pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 380, 70, 30),
    "FASTER": pygame.Rect(GRID_SIZE * GRID_WIDTH + 110, 380, 70, 30),
}

PAUSE_BUTTON = pygame.Rect(GRID_SIZE * GRID_WIDTH + 20, 450, 160, 40)


class TetrisGame:
    def __init__(self):
        self.reset_game()
        self.game_speed = 5  # Default speed
        self.fall_time = 0
        self.key_delay = 200  # Delay in milliseconds
        self.last_key_press_time = pygame.time.get_ticks()
        self.paused = False

    def reset_game(self):
        self.grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.select_new_tetromino()
        self.next_tetromino = self.get_random_tetromino()
        self.score = 0
        self.game_over = False

    def get_random_tetromino(self):
        key = random.choice(list(TETROMINOES.keys()))
        return TETROMINOES[key]

    def select_new_tetromino(self):
        self.current_tetromino_key = random.choice(list(TETROMINOES.keys()))
        tetromino_data = TETROMINOES[self.current_tetromino_key]
        self.current_tetromino = tetromino_data["shape"]
        self.current_color = tetromino_data["color"]
        self.offset_x = GRID_WIDTH // 2 - len(self.current_tetromino[0]) // 2
        self.offset_y = 0

    def check_collision(self, tetromino, offset_x, offset_y):
        for i, row in enumerate(tetromino):
            for j, cell in enumerate(row):
                if cell:
                    if (
                        offset_x + j < 0
                        or offset_x + j >= GRID_WIDTH
                        or offset_y + i >= GRID_HEIGHT
                        or (
                            0 <= offset_y + i < GRID_HEIGHT
                            and self.grid[offset_y + i][offset_x + j]
                        )
                    ):
                        return True
        return False

    def lock_tetromino(self):
        for i, row in enumerate(self.current_tetromino):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.offset_y + i][self.offset_x + j] = True

    def clear_lines(self):
        new_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        line_count = 0
        row = GRID_HEIGHT - 1

        for r in range(GRID_HEIGHT - 1, -1, -1):
            if all(self.grid[r]):
                line_count += 1
            else:
                new_grid[row] = self.grid[r]
                row -= 1

        self.grid = new_grid
        self.score += line_count * 10

    def rotate_tetromino(self):
        rotated = list(zip(*reversed(self.current_tetromino)))
        if not self.check_collision(rotated, self.offset_x, self.offset_y):
            self.current_tetromino = rotated

    def handle_input(self, x=-1, y=-1, keys=None):
        if self.game_over or self.paused:
            return

        # Handle mouse clicks on control buttons
        if x != -1 and y != -1:
            if CONTROL_BUTTONS["LEFT"].collidepoint(x, y):
                if not self.check_collision(
                    self.current_tetromino, self.offset_x - 1, self.offset_y
                ):
                    self.offset_x -= 1
            elif CONTROL_BUTTONS["RIGHT"].collidepoint(x, y):
                if not self.check_collision(
                    self.current_tetromino, self.offset_x + 1, self.offset_y
                ):
                    self.offset_x += 1
            elif CONTROL_BUTTONS["DOWN"].collidepoint(x, y):
                if not self.check_collision(
                    self.current_tetromino, self.offset_x, self.offset_y + 1
                ):
                    self.offset_y += 1
            elif CONTROL_BUTTONS["ROTATE"].collidepoint(x, y):
                self.rotate_tetromino()
            elif SPEED_BUTTONS["SLOWER"].collidepoint(x, y):
                if self.game_speed > 1:
                    self.game_speed -= 1
            elif SPEED_BUTTONS["FASTER"].collidepoint(x, y):
                if self.game_speed < 10:
                    self.game_speed += 1
            elif PAUSE_BUTTON.collidepoint(x, y):
                self.paused = not self.paused

        # Handle keyboard controls
        if keys:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_key_press_time > self.key_delay:
                if keys[pygame.K_LEFT] and not self.check_collision(
                    self.current_tetromino, self.offset_x - 1, self.offset_y
                ):
                    self.offset_x -= 1
                    self.last_key_press_time = current_time
                elif keys[pygame.K_RIGHT] and not self.check_collision(
                    self.current_tetromino, self.offset_x + 1, self.offset_y
                ):
                    self.offset_x += 1
                    self.last_key_press_time = current_time
                elif keys[pygame.K_DOWN] and not self.check_collision(
                    self.current_tetromino, self.offset_x, self.offset_y + 1
                ):
                    self.offset_y += 1
                    self.last_key_press_time = current_time
                elif keys[pygame.K_r] or keys[pygame.K_UP]:
                    self.rotate_tetromino()
                    self.last_key_press_time = current_time

    def update(self, dt):
        if self.game_over or self.paused:
            return

        self.fall_time += dt
        fall_speed = 1000 - (self.game_speed * 90)  # Higher speed = faster fall

        if self.fall_time > fall_speed:
            self.fall_time = 0
            if not self.check_collision(
                self.current_tetromino, self.offset_x, self.offset_y + 1
            ):
                self.offset_y += 1
            else:
                self.lock_tetromino()
                self.clear_lines()
                self.select_new_tetromino()
                if self.check_collision(
                    self.current_tetromino, self.offset_x, self.offset_y
                ):
                    self.game_over = True

    def draw(self):
        # Clear screen
        screen.fill(BACKGROUND_COLOR)

        # Draw grid and locked tetrominoes
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    pygame.draw.rect(
                        screen,
                        WHITE,
                        (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
                    )

        # Draw current tetromino
        if not self.game_over:
            self.draw_tetromino()

        # Draw grid lines
        for x in range(0, GRID_SIZE * GRID_WIDTH + 1, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (x, 0), (x, GRID_SIZE * GRID_HEIGHT))
        for y in range(0, GRID_SIZE * GRID_HEIGHT + 1, GRID_SIZE):
            pygame.draw.line(screen, WHITE, (0, y), (GRID_SIZE * GRID_WIDTH, y))

        # Draw UI elements
        self.draw_buttons()
        self.draw_speed_controls()
        self.draw_score()
        self.draw_next_tetromino()

        if self.game_over:
            return self.draw_game_over_dialog()
        return None, None

    def draw_tetromino(self):
        for i, row in enumerate(self.current_tetromino):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        self.current_color,
                        (
                            (self.offset_x + j) * GRID_SIZE,
                            (self.offset_y + i) * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                    )
                    pygame.draw.rect(
                        screen,
                        BLACK,
                        (
                            (self.offset_x + j) * GRID_SIZE,
                            (self.offset_y + i) * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                        1,
                    )

    def draw_buttons(self):
        for name, rect in CONTROL_BUTTONS.items():
            pygame.draw.rect(screen, WHITE, rect, border_radius=5)
            text = FONT_MEDIUM.render(name, True, BLACK)
            screen.blit(text, (rect.x + 20, rect.y + 15))

        pygame.draw.rect(screen, WHITE, PAUSE_BUTTON, border_radius=5)
        pause_text = FONT_MEDIUM.render("PAUSE", True, BLACK)
        screen.blit(pause_text, (PAUSE_BUTTON.x + 20, PAUSE_BUTTON.y + 15))

    def draw_speed_controls(self):
        text = FONT_SMALL.render("Speed:", True, WHITE)
        screen.blit(text, (GRID_SIZE * GRID_WIDTH + 20, 350))

        # Draw speed buttons
        pygame.draw.rect(screen, WHITE, SPEED_BUTTONS["SLOWER"], border_radius=5)
        pygame.draw.rect(screen, WHITE, SPEED_BUTTONS["FASTER"], border_radius=5)

        minus_text = FONT_SMALL.render("Slower", True, BLACK)
        plus_text = FONT_SMALL.render("Faster", True, BLACK)

        screen.blit(
            minus_text, (SPEED_BUTTONS["SLOWER"].x + 5, SPEED_BUTTONS["SLOWER"].y + 5)
        )
        screen.blit(
            plus_text, (SPEED_BUTTONS["FASTER"].x + 5, SPEED_BUTTONS["FASTER"].y + 5)
        )

        # Current speed
        text = FONT_SMALL.render(f"Level: {self.game_speed}", True, WHITE)
        screen.blit(text, (GRID_SIZE * GRID_WIDTH + 20, 420))

    def draw_score(self):
        text = FONT_MEDIUM.render(f"Score: {self.score}", True, WHITE)
        screen.blit(text, (GRID_SIZE * GRID_WIDTH + 20, 300))

    def draw_next_tetromino(self):
        text = FONT_MEDIUM.render("Next:", True, WHITE)
        screen.blit(text, (GRID_SIZE * GRID_WIDTH + 20, 500))

        for i, row in enumerate(self.next_tetromino["shape"]):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        self.next_tetromino["color"],
                        (
                            GRID_SIZE * GRID_WIDTH + 20 + j * GRID_SIZE,
                            540 + i * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                    )
                    pygame.draw.rect(
                        screen,
                        BLACK,
                        (
                            GRID_SIZE * GRID_WIDTH + 20 + j * GRID_SIZE,
                            540 + i * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                        1,
                    )

    def draw_game_over_dialog(self):
        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Dialog box
        dialog_width, dialog_height = 300, 200
        dialog_x = (SCREEN_WIDTH - dialog_width) // 2
        dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

        pygame.draw.rect(
            screen,
            WHITE,
            (dialog_x, dialog_y, dialog_width, dialog_height),
            border_radius=10,
        )
        pygame.draw.rect(
            screen,
            BLACK,
            (dialog_x, dialog_y, dialog_width, dialog_height),
            2,
            border_radius=10,
        )

        # Game Over text
        game_over_text = FONT_LARGE.render("Game Over", True, BLACK)
        text_width = game_over_text.get_width()
        screen.blit(
            game_over_text, (dialog_x + (dialog_width - text_width) // 2, dialog_y + 30)
        )

        # Score text
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, BLACK)
        text_width = score_text.get_width()
        screen.blit(
            score_text, (dialog_x + (dialog_width - text_width) // 2, dialog_y + 80)
        )

        # Buttons
        restart_button = pygame.Rect(dialog_x + 30, dialog_y + 130, 100, 40)
        quit_button = pygame.Rect(dialog_x + 170, dialog_y + 130, 100, 40)

        pygame.draw.rect(screen, GREEN, restart_button, border_radius=5)
        pygame.draw.rect(screen, RED, quit_button, border_radius=5)

        restart_text = FONT_SMALL.render("Restart", True, BLACK)
        quit_text = FONT_SMALL.render("Quit", True, BLACK)

        screen.blit(
            restart_text,
            (
                restart_button.x
                + (restart_button.width - restart_text.get_width()) // 2,
                restart_button.y
                + (restart_button.height - restart_text.get_height()) // 2,
            ),
        )
        screen.blit(
            quit_text,
            (
                quit_button.x + (quit_button.width - quit_text.get_width()) // 2,
                quit_button.y + (quit_button.height - quit_text.get_height()) // 2,
            ),
        )

        return restart_button, quit_button


def main():
    game = TetrisGame()
    running = True

    while running:
        dt = clock.tick(60)  # Get time since last tick in milliseconds
        mouse_x, mouse_y = -1, -1  # Initialize mouse position

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

        # Handle inputs and update game state
        if game.game_over:
            restart_button, quit_button = game.draw()
            if mouse_x != -1 and mouse_y != -1:
                if restart_button and restart_button.collidepoint(mouse_x, mouse_y):
                    game.reset_game()
                elif quit_button and quit_button.collidepoint(mouse_x, mouse_y):
                    running = False
        else:
            game.handle_input(mouse_x, mouse_y, pygame.key.get_pressed())
            game.update(dt)
            game.draw()

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
