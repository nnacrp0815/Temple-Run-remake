"""Temple Run-inspired endless runner prototype using Pygame.

Run the game with `python main.py` once you have installed the dependencies in
`requirements.txt`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import pygame

# Screen configuration
WIDTH, HEIGHT = 960, 540
GROUND_Y = int(HEIGHT * 0.75)
FPS = 60

# Player configuration
PLAYER_WIDTH, PLAYER_HEIGHT = 60, 90
JUMP_VELOCITY = -22
GRAVITY = 1.2
SLIDE_DURATION_FRAMES = int(0.6 * FPS)
SLIDE_HEIGHT = 45

# Obstacle configuration
OBSTACLE_SPEED_START = 8
OBSTACLE_ACCELERATION = 0.005  # Speed increase per frame
OBSTACLE_SPAWN_MIN = 60  # Minimum frames between spawns
OBSTACLE_SPAWN_MAX = 160

# Colors
SKY = (35, 45, 60)
GROUND = (65, 50, 35)
PLAYER_COLOR = (255, 210, 60)
PLAYER_SHADOW = (200, 160, 40)
OBSTACLE_COLOR = (200, 80, 60)
TEXT_COLOR = (245, 245, 245)


class Player:
    """Represents the player character."""

    def __init__(self) -> None:
        self.rect = pygame.Rect(WIDTH // 4, GROUND_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_y = 0.0
        self.on_ground = True
        self.sliding_frames_left = 0

    def start_jump(self) -> None:
        if self.on_ground and self.sliding_frames_left == 0:
            self.velocity_y = JUMP_VELOCITY
            self.on_ground = False

    def start_slide(self) -> None:
        if self.on_ground and self.sliding_frames_left == 0:
            self.sliding_frames_left = SLIDE_DURATION_FRAMES
            self.rect.height = SLIDE_HEIGHT
            self.rect.y = GROUND_Y - SLIDE_HEIGHT

    def update(self) -> None:
        if self.sliding_frames_left > 0:
            self.sliding_frames_left -= 1
            if self.sliding_frames_left == 0:
                self.rect.height = PLAYER_HEIGHT
                self.rect.y = GROUND_Y - PLAYER_HEIGHT
        else:
            self.velocity_y += GRAVITY
            self.rect.y += int(self.velocity_y)
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.velocity_y = 0
                self.on_ground = True
            else:
                self.on_ground = False

    def draw(self, surface: pygame.Surface) -> None:
        body_rect = self.rect.copy()
        pygame.draw.rect(surface, PLAYER_SHADOW, body_rect.inflate(10, 10))
        pygame.draw.rect(surface, PLAYER_COLOR, body_rect)


@dataclass
class Obstacle:
    """Obstacles the player must avoid."""

    rect: pygame.Rect
    speed: float

    @classmethod
    def spawn(cls, speed: float) -> "Obstacle":
        kind = random.choice(["low", "high"])
        if kind == "low":
            width, height = 50, 120
            y = GROUND_Y - height
        else:
            width, height = 50, 60
            y = GROUND_Y - height - PLAYER_HEIGHT + SLIDE_HEIGHT
        rect = pygame.Rect(WIDTH + 10, y, width, height)
        return cls(rect=rect, speed=speed)

    def update(self) -> None:
        self.rect.x -= int(self.speed)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect)

    def is_offscreen(self) -> bool:
        return self.rect.right < 0


class Scoreboard:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.distance = 0.0
        self.best_distance = 0.0

    def reset(self) -> None:
        self.distance = 0.0

    def update(self, speed: float) -> None:
        # Distance scaled so higher speed gives more points.
        self.distance += speed * 0.1
        self.best_distance = max(self.best_distance, self.distance)

    def draw(self, surface: pygame.Surface) -> None:
        score_text = f"Score: {int(self.distance):05d}   Best: {int(self.best_distance):05d}"
        text_surface = self.font.render(score_text, True, TEXT_COLOR)
        surface.blit(text_surface, (20, 20))


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Temple Run-Inspired Prototype")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        font_path = Path(pygame.font.get_default_font())
        self.font = pygame.font.Font(font_path, 28)

        self.player = Player()
        self.obstacles: list[Obstacle] = []
        self.obstacle_timer = 0
        self.speed = OBSTACLE_SPEED_START
        self.score = Scoreboard(self.font)
        self.running = True
        self.game_over = False

    def reset(self) -> None:
        self.player = Player()
        self.obstacles.clear()
        self.obstacle_timer = 0
        self.speed = OBSTACLE_SPEED_START
        self.score.reset()
        self.game_over = False

    def spawn_obstacle(self) -> None:
        self.obstacles.append(Obstacle.spawn(self.speed))
        self.obstacle_timer = random.randint(OBSTACLE_SPAWN_MIN, OBSTACLE_SPAWN_MAX)

    def handle_input(self) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.game_over:
                self.reset()
            else:
                self.player.start_jump()
        if keys[pygame.K_LSHIFT] and not self.game_over:
            self.player.start_slide()

    def update(self) -> None:
        self.handle_input()

        if not self.game_over:
            self.player.update()
            self.speed += OBSTACLE_ACCELERATION
            self.score.update(self.speed)

            if self.obstacle_timer <= 0:
                self.spawn_obstacle()
            else:
                self.obstacle_timer -= 1

            for obstacle in list(self.obstacles):
                obstacle.speed = self.speed
                obstacle.update()
                if obstacle.is_offscreen():
                    self.obstacles.remove(obstacle)

            if any(self.player.rect.colliderect(obs.rect) for obs in self.obstacles):
                self.game_over = True

    def draw_ground(self) -> None:
        pygame.draw.rect(self.screen, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        for x in range(0, WIDTH, 80):
            pygame.draw.rect(self.screen, (80, 60, 40), (x, GROUND_Y - 10, 60, 10))

    def draw_game_over(self) -> None:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        text_lines = [
            "Run Over!",
            "Press Space to try again",
        ]
        for index, line in enumerate(text_lines):
            text_surface = self.font.render(line, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + index * 40))
            self.screen.blit(text_surface, text_rect)

    def draw(self) -> None:
        self.screen.fill(SKY)
        self.draw_ground()
        self.player.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.score.draw(self.screen)
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
