import random
import pygame
from entities import RectObstacle, MineCart


def _load_cart_sprite():
    # Optional: if you later add assets, this will auto-use them.
    # Put something like: ../assets/sprites/props/mine_cart.png
    try:
        return pygame.image.load("../assets/sprites/props/mine_cart.png").convert_alpha()
    except Exception:
        return None


class TunnelSpawner:
    """
    Walkable continuous tunnel:
    - wide overlapping wall segments => solid corridor look
    - walls are SOLID but NOT lethal (walkable)
    - corridor center drifts smoothly (no abrupt jumps)
    - spawns lethal mine carts on the FLOOR that you must jump over
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.spawn_timer = 0.0

        self.base_velocity = 520.0
        self.gap = 240

        # Wide panels to look solid
        self.panel_width = 160
        self.overlap_px = 3
        self.panel_rate = 0.20

        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

        self.target_timer = 0.0
        self.target_interval = 0.60
        self.follow = 0.10

        # ---- carts ----
        self.cart_sprite = _load_cart_sprite()
        self.cart_timer = 0.0
        self.cart_cooldown = 3.8  # seconds between carts at tier 0 (sparse early)

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.target_timer = 0.0

        H = self.screen.get_height()
        self.gap_center = H // 2
        self.target_center = self.gap_center

        self.cart_timer = 0.0
        self.cart_cooldown = 3.8

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.base_velocity = 520.0 + tier * 26.0
        self.gap = max(170, 240 - tier * 7)

        # keep it solid-looking at higher speeds: spawn panels a bit faster
        self.panel_rate = max(0.14, 0.20 - tier * 0.004)

        self.target_interval = max(0.42, 0.60 - tier * 0.01)
        self.follow = min(0.16, 0.10 + tier * 0.004)

        # carts get more common slowly (but never spammy)
        # tier 0: ~3.8s, tier 10: ~2.8s, tier 20: ~2.0s
        self.cart_cooldown = max(1.8, 3.8 - tier * 0.10)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.target_timer += dt
        self.cart_timer += dt

        H = self.screen.get_height()
        margin = 80

        # occasionally choose a new target center (bounded, non-abrupt)
        if self.target_timer >= self.target_interval:
            self.target_timer = 0.0

            min_c = margin + self.gap // 2
            max_c = (H - margin) - self.gap // 2

            step = random.randint(-140, 140)
            self.target_center = max(min_c, min(max_c, self.target_center + step))

        # smooth drift
        self.gap_center = int(
            self.gap_center + (self.target_center - self.gap_center) * self.follow
        )

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.panel_rate

    def _maybe_spawn_cart(self, tier: int, x: int, floor_y: int) -> list[MineCart]:
        """
        Spawn a lethal cart on the tunnel floor occasionally.
        The player is X-locked, so this is a vertical timing challenge: jump over.
        """
        if self.cart_timer < self.cart_cooldown:
            return []

        # Reset timer with a little jitter so it doesn’t feel metronomic
        self.cart_timer = 0.0
        self.cart_cooldown *= random.uniform(0.85, 1.15)

        # Cart geometry (tuned to be jumpable with your current physics)
        cart_w = 70
        cart_h = 36

        # Keep carts from becoming unfair if gap is tight
        # If the gap is too small, reduce cart height slightly
        if self.gap < 190:
            cart_h = 32

        cart_x = x + self.panel_width + random.randint(180, 320)
        cart_y = floor_y - cart_h  # sits ON the floor

        # Slightly faster than walls so it “approaches” more aggressively
        cart_v = self.base_velocity * 1.10

        return [
            MineCart(
                screen=self.screen,
                rect=pygame.Rect(cart_x, cart_y, cart_w, cart_h),
                velocity=cart_v,
                sprite=self.cart_sprite,
            )
        ]

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        # overlap the next segment slightly so it looks continuous
        x = W + 20 - self.overlap_px

        top_h = max(0, self.gap_center - self.gap // 2)
        bot_y = self.gap_center + self.gap // 2  # top of floor block (walkable surface)
        bot_h = max(0, H - bot_y)

        # Non-lethal SOLID walls
        top_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, self.panel_width + self.overlap_px, top_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )
        bottom_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, bot_y, self.panel_width + self.overlap_px, bot_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )

        obstacles = [top_wall, bottom_wall]

        # Add carts on floor occasionally
        obstacles.extend(self._maybe_spawn_cart(tier=tier, x=x, floor_y=bot_y))

        self.spawn_timer = 0.0
        return obstacles, []
