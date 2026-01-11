import random
import pygame

from entities import Pipe
from entities import Coin
from entities import HazardPatch


def _load_pipe_sprites():
    sprites = []
    v1 = pygame.image.load("../assets/sprites/pipeSprites/pipeVariant1.png").convert_alpha()
    v2 = pygame.image.load("../assets/sprites/pipeSprites/pipeVariant2.png").convert_alpha()
    sprites.append(v1)
    sprites.append(v2)
    return sprites


def _choose(sprites):
    return sprites[random.randint(0, len(sprites) - 1)]


def _load_coin_sprite():
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


class SpikesSpawner:
    """
    Spikes section:
    - fixed difficulty per section (tier)
    - coins spawn only every few obstacles
    - lava appears as floor patches between certain spikes (not rising)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sprites = _load_pipe_sprites()
        self.coin_sprite = _load_coin_sprite()

        self.spawn_timer = 0.0
        self.spawn_rate = 0.85
        self.base_velocity = 500.0
        self.edge = int(self.screen.get_height() * 0.05)

        self.spawn_patterns = [
            ["top", "bottom"],
            ["bottom", "top", "bottom", "top"],
            ["top", "bottom", "top"],
            ["bottom", "top"],
        ]
        self.curr_pattern = random.choice(self.spawn_patterns)
        self.pattern_idx = 0

        # Coin throttling
        self.obstacles_since_coin = 0
        self.next_coin_in = random.randint(3, 6)  # 1 coin every 3-6 obstacles

        # Hazard intensity is provided by progression each spawn
        self.hazard_intensity = 0.0

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.curr_pattern = random.choice(self.spawn_patterns)
        self.pattern_idx = 0

        self.obstacles_since_coin = 0
        self.next_coin_in = random.randint(3, 6)

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))
        self.base_velocity = 500.0 + tier * 35.0
        self.spawn_rate = max(0.55, 0.85 - tier * 0.03)

    def setHazardIntensity(self, hazard_intensity: float) -> None:
        self.hazard_intensity = max(0.0, min(1.0, float(hazard_intensity)))

    def update(self, dt: float) -> None:
        self.spawn_timer += dt

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.spawn_rate

    def spawn(self, tier: int) -> tuple[list, list[Coin]]:
        """
        Returns:
          obstacles: list of Pipe and/or HazardPatch
          coins: list of Coin
        """
        self.setDifficultyTier(tier)

        orientation = self.curr_pattern[self.pattern_idx]
        self.pattern_idx += 1
        if self.pattern_idx >= len(self.curr_pattern):
            self.curr_pattern = random.choice(self.spawn_patterns)
            self.pattern_idx = 0

        W = self.screen.get_width()
        H = self.screen.get_height()

        newX = W + 20
        height = Pipe.Proportions.BASE_HEIGHT.value

        # spike y placement
        if orientation == "top":
            newY = random.randint(-self.edge, 0)
        else:
            newY = random.randint(H - height, H - self.edge)

        pipe = Pipe(
            screen=self.screen,
            currPos=pygame.Vector2(newX, newY),
            velocity=self.base_velocity,
            orientation=orientation,
            sprite=_choose(self.sprites),
        )

        obstacles = [pipe]
        coins: list[Coin] = []

        # coins - only once every few obstacles
        self.obstacles_since_coin += 1
        if self.obstacles_since_coin >= self.next_coin_in:
            self.obstacles_since_coin = 0
            self.next_coin_in = random.randint(3, 6)

            # place 1 coin in a “tempting but fair” position
            coin_x = newX + Pipe.Proportions.WIDTH.value + random.randint(70, 140)

            # bias coin away from immediate spike body
            if orientation == "top":
                coin_y = random.randint(int(H * 0.45), int(H * 0.80))
            else:
                coin_y = random.randint(int(H * 0.20), int(H * 0.55))

            coins.append(
                Coin(
                    screen=self.screen,
                    pos=pygame.Vector2(coin_x, coin_y),
                    radius=13,
                    value=1,
                    velocity=self.base_velocity,
                    sprite=self.coin_sprite,
                )
            )

            # rare gold coin (still respects “few coins” rule)
            if random.random() < 0.12:
                coins.append(
                    Coin(
                        screen=self.screen,
                        pos=pygame.Vector2(coin_x + 60, coin_y - 25),
                        radius=15,
                        value=5,
                        velocity=self.base_velocity,
                        sprite=self.coin_sprite,
                    )
                )

        # Lava patches - floor kill-zones between certain spikes
        # probability increases with hazard_intensity
        # Start very low; becomes common later.
        lava_chance = 0.03 + 0.35 * (self.hazard_intensity ** 1.4)

        if random.random() < lava_chance:
            patch_width = random.randint(int(W * 0.10), int(W * 0.20))
            patch_height = random.randint(26, 42)  # fixed-ish, not rising
            patch_x = newX + Pipe.Proportions.WIDTH.value + random.randint(120, 260)
            patch_y = H - patch_height

            obstacles.append(
                HazardPatch(
                    screen=self.screen,
                    rect=pygame.Rect(patch_x, patch_y, patch_width, patch_height),
                    velocity=self.base_velocity,
                    color="orangered3",
                )
            )

        # (optional) ceiling danger later: “toxic ceiling” patches
        ceil_chance = 0.00 + 0.22 * max(0.0, (self.hazard_intensity - 0.55) / 0.45) ** 1.3
        if random.random() < ceil_chance:
            patch_width = random.randint(int(W * 0.10), int(W * 0.18))
            patch_height = random.randint(22, 36)
            patch_x = newX + Pipe.Proportions.WIDTH.value + random.randint(140, 280)
            patch_y = 0

            obstacles.append(
                HazardPatch(
                    screen=self.screen,
                    rect=pygame.Rect(patch_x, patch_y, patch_width, patch_height),
                    velocity=self.base_velocity,
                    color="indianred4",
                )
            )

        self.spawn_timer = 0.0
        return obstacles, coins
