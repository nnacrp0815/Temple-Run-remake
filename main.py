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

# Power-up configuration
COIN_COOLDOWN_FRAMES = 15 * FPS
GUN_DURATION_FRAMES = 15 * FPS
BULLET_SPEED = 22

# Colors
SKY = (35, 45, 60)
GROUND = (65, 50, 35)
OBSTACLE_COLOR = (200, 80, 60)
TEXT_COLOR = (245, 245, 245)
COIN_COLOR = (255, 215, 0)
BULLET_COLOR = (120, 200, 255)

# Player palette (Minecraft Steve inspired)
STEVE_SKIN = (204, 172, 141)
STEVE_SHIRT = (58, 142, 186)
STEVE_PANTS = (43, 60, 86)
STEVE_SHOES = (45, 36, 30)
STEVE_HAIR = (70, 50, 35)


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

    def is_sliding(self) -> bool:
        return self.sliding_frames_left > 0

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

        # Draw subtle drop shadow for depth.
        shadow_rect = body_rect.inflate(12, 12)
        shadow_rect.y += 6
        pygame.draw.rect(surface, (30, 30, 30), shadow_rect)

        # Head
        head_height = max(int(body_rect.height * 0.27), 8)
        head_width = max(int(body_rect.width * 0.6), 20)
        head_rect = pygame.Rect(
            body_rect.centerx - head_width // 2,
            body_rect.y,
            head_width,
            head_height,
        )
        hair_rect = pygame.Rect(head_rect.x, head_rect.y, head_rect.width, max(head_height // 3, 4))

        # Torso and arms
        torso_height = max(int(body_rect.height * 0.36), 12)
        torso_rect = pygame.Rect(
            body_rect.centerx - head_width // 2,
            head_rect.bottom,
            head_width,
            torso_height,
        )
        arms_height = max(int(body_rect.height * 0.28), 10)
        arms_rect = pygame.Rect(
            body_rect.x,
            head_rect.bottom,
            body_rect.width,
            arms_height,
        )

        # Legs/Shoes
        legs_height = max(body_rect.bottom - torso_rect.bottom, 6)
        leg_width = max(head_width // 2, 18)
        left_leg = pygame.Rect(
            torso_rect.x,
            torso_rect.bottom,
            leg_width // 2,
            legs_height,
        )
        right_leg = pygame.Rect(
            torso_rect.right - leg_width // 2,
            torso_rect.bottom,
            leg_width // 2,
            legs_height,
        )

        left_shoe = left_leg.copy()
        left_shoe.height = max(left_leg.height // 3, 4)
        left_shoe.y = left_leg.bottom - left_shoe.height
        right_shoe = right_leg.copy()
        right_shoe.height = max(right_leg.height // 3, 4)
        right_shoe.y = right_leg.bottom - right_shoe.height

        pygame.draw.rect(surface, STEVE_SHIRT, torso_rect)
        pygame.draw.rect(surface, STEVE_SHIRT, arms_rect)
        pygame.draw.rect(surface, STEVE_SKIN, head_rect)
        pygame.draw.rect(surface, STEVE_HAIR, hair_rect)
        pygame.draw.rect(surface, STEVE_PANTS, left_leg)
        pygame.draw.rect(surface, STEVE_PANTS, right_leg)
        pygame.draw.rect(surface, STEVE_SHOES, left_shoe)
        pygame.draw.rect(surface, STEVE_SHOES, right_shoe)

        if self.is_sliding():
            # Add a simple motion streak to emphasize sliding.
            streak = pygame.Rect(body_rect.x - 10, body_rect.bottom - 8, 10, 6)
            pygame.draw.rect(surface, STEVE_PANTS, streak)


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


@dataclass
class Coin:
    rect: pygame.Rect
    speed: float

    @classmethod
    def spawn(cls, speed: float) -> "Coin":
        size = 36
        kind = random.choice(["low", "high"])
        if kind == "low":
            y = GROUND_Y - size - 20
        else:
            y = GROUND_Y - PLAYER_HEIGHT - size
        rect = pygame.Rect(WIDTH + 10, y, size, size)
        return cls(rect=rect, speed=speed)

    def update(self) -> None:
        self.rect.x -= int(self.speed)

    def draw(self, surface: pygame.Surface) -> None:
        center = self.rect.center
        radius = self.rect.width // 2
        pygame.draw.circle(surface, (255, 170, 0), center, radius)
        inner_radius = max(radius - 6, 4)
        pygame.draw.circle(surface, COIN_COLOR, center, inner_radius)

    def is_offscreen(self) -> bool:
        return self.rect.right < 0


@dataclass
class Bullet:
    rect: pygame.Rect
    speed: float

    def update(self) -> None:
        self.rect.x += int(self.speed)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BULLET_COLOR, self.rect)

    def is_offscreen(self) -> bool:
        return self.rect.left > WIDTH


class Scoreboard:
    def __init__(self, font: pygame.font.Font) -> None:
        self.font = font
        self.base_points = 0.0
        self.bonus_points = 0
        self.best_score = 0

    def reset(self) -> None:
        self.base_points = 0.0
        self.bonus_points = 0

    def update(self, speed: float) -> None:
        # Distance scaled so higher speed gives more points.
        self.base_points += speed * 0.1
        self.best_score = max(self.best_score, self.total_score())

    def add_bonus(self, points: int) -> None:
        self.bonus_points += points
        self.best_score = max(self.best_score, self.total_score())

    def total_score(self) -> int:
        return int(self.base_points + self.bonus_points)

    def draw(self, surface: pygame.Surface) -> None:
        score_text = f"Score: {self.total_score():05d}   Best: {int(self.best_score):05d}"
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
        self.coin: Coin | None = None
        self.coin_cooldown = COIN_COOLDOWN_FRAMES
        self.gun_timer = 0
        self.bullets: list[Bullet] = []

    def reset(self) -> None:
        self.player = Player()
        self.obstacles.clear()
        self.obstacle_timer = 0
        self.speed = OBSTACLE_SPEED_START
        self.score.reset()
        self.game_over = False
        self.coin = None
        self.coin_cooldown = COIN_COOLDOWN_FRAMES
        self.gun_timer = 0
        self.bullets.clear()

    def spawn_obstacle(self) -> None:
        self.obstacles.append(Obstacle.spawn(self.speed))
        self.obstacle_timer = random.randint(OBSTACLE_SPAWN_MIN, OBSTACLE_SPAWN_MAX)

    def spawn_coin(self) -> None:
        self.coin = Coin.spawn(self.speed)
        self.coin_cooldown = COIN_COOLDOWN_FRAMES

    def fire_bullet(self) -> None:
        if self.game_over or self.gun_timer <= 0:
            return
        bullet_rect = pygame.Rect(
            self.player.rect.right,
            self.player.rect.centery - 4,
            24,
            8,
        )
        self.bullets.append(Bullet(rect=bullet_rect, speed=BULLET_SPEED))

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
                self.gun_timer = 0
                self.coin = None

            self.update_coin()
            self.update_bullets()

    def update_coin(self) -> None:
        if self.gun_timer > 0:
            self.gun_timer -= 1

        if self.coin is None:
            if self.gun_timer <= 0:
                if self.coin_cooldown > 0:
                    self.coin_cooldown -= 1
                else:
                    self.spawn_coin()
        else:
            self.coin.speed = self.speed
            self.coin.update()
            if self.coin.is_offscreen():
                self.coin = None
                self.coin_cooldown = COIN_COOLDOWN_FRAMES
            elif self.player.rect.colliderect(self.coin.rect):
                self.coin = None
                self.gun_timer = GUN_DURATION_FRAMES
                self.coin_cooldown = COIN_COOLDOWN_FRAMES

    def update_bullets(self) -> None:
        for bullet in list(self.bullets):
            bullet.update()
            if bullet.is_offscreen():
                self.bullets.remove(bullet)
                continue

            hit_obstacle = next((obs for obs in self.obstacles if bullet.rect.colliderect(obs.rect)), None)
            if hit_obstacle is not None:
                if hit_obstacle in self.obstacles:
                    self.obstacles.remove(hit_obstacle)
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                self.score.add_bonus(500)

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
        if self.coin is not None:
            self.coin.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        self.score.draw(self.screen)
        if self.gun_timer > 0:
            seconds_left = self.gun_timer / FPS
            gun_text = f"Gun active: {seconds_left:0.1f}s  (Press Enter to shoot)"
            text_surface = self.font.render(gun_text, True, TEXT_COLOR)
            self.screen.blit(text_surface, (20, 60))
        if self.game_over:
            self.draw_game_over()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_RETURN:
                        self.fire_bullet()

            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
