import random
import pygame

from entities import RectObstacle, MineCart, Coin
import gameplay.tunnel_field as tunnel_field


def _load_cart_sprite():
    try:
        return pygame.image.load("../assets/sprites/props/mine_cart.png").convert_alpha()
    except Exception:
        return None


def _load_coin_sprite():
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class TunnelSpawner:
    """
    Walkable tunnel with gentle slopes.
    - Player auto-climbs via standard solid resolution.
    - We generate occasional flat platform stretches where minecarts can spawn.
    - On slopes, we instead generate stalactites/stalagmites (lethal spikes),
      while guaranteeing the corridor remains passable.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # World speed (panels)
        self.base_velocity = 520.0

        # Panel geometry
        self.panel_width = 180
        self.overlap_px = 4
        self.panel_rate = 0.22
        self.spawn_timer = 0.0

        # Tunnel shape
        H = self.screen.get_height()
        self.gap = 240
        self.min_corridor = 175  # never go below this in tunnel

        self.floor_y = int(H * 0.70)  # top of bottom wall
        self.ceiling_y = int(H * 0.25)  # bottom of top wall

        # Slope control
        self.slope_per_panel = 10  # pixels per panel (gentle)
        self.slope_dir = 0         # -1 up (floor goes up), +1 down (floor goes down), 0 flat

        self.target_timer = 0.0
        self.target_interval = 0.85  # how often we reconsider direction

        # Flat-run scheduling (for carts)
        self.force_flat_panels_left = 0
        self.flat_run_min = 6
        self.flat_run_max = 10
        self.next_flat_in_panels = random.randint(10, 16)
        self.panels_since_flat = 0

        # Carts
        self.cart_sprite = _load_cart_sprite()
        self.cart_speed_mult = 1.30
        self.cart_cooldown_panels = 7  # at most one cart per flat run
        self.cart_ready_in = 0

        # Coins
        self.coin_sprite = _load_coin_sprite()
        self.panels_since_coin = 0
        self.next_coin_in = random.randint(4, 7)

        # Floor field for carts
        if tunnel_field.TUNNEL_FIELD is None:
            tunnel_field.TUNNEL_FIELD = tunnel_field.TunnelField(
                screen_width=self.screen.get_width(),
                default_floor_y=self.screen.get_height(),
                sample_step=4,
            )

    def reset(self) -> None:
        H = self.screen.get_height()
        self.gap = 240
        self.floor_y = int(H * 0.70)
        self.ceiling_y = int(H * 0.25)

        self.spawn_timer = 0.0
        self.target_timer = 0.0

        self.slope_dir = 0
        self.force_flat_panels_left = 0
        self.next_flat_in_panels = random.randint(10, 16)
        self.panels_since_flat = 0

        self.cart_ready_in = 0

        self.panels_since_coin = 0
        self.next_coin_in = random.randint(4, 7)

        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.reset()

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.base_velocity = 520.0 + tier * 26.0
        self.gap = max(self.min_corridor, 240 - tier * 6)

        # Slightly denser panels as speed increases
        self.panel_rate = max(0.16, 0.22 - tier * 0.003)

        # Slightly more slope later, but still controlled
        self.slope_per_panel = int(_clamp(10 + tier * 0.3, 10, 14))

        # Flat runs a bit shorter later, but still present
        self.flat_run_min = max(5, 6 - tier // 10)
        self.flat_run_max = max(self.flat_run_min, 10 - tier // 8)

        # Carts a bit more frequent later (but only in flats)
        self.cart_cooldown_panels = max(5, 7 - tier // 8)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.target_timer += dt

        # Shift floor field with WORLD velocity
        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.update(dt, self.base_velocity)

        # Decide slope direction occasionally unless we are forcing a flat run
        if self.force_flat_panels_left <= 0 and self.target_timer >= self.target_interval:
            self.target_timer = 0.0

            # Weighted: mostly gentle slopes, sometimes flat
            r = random.random()
            if r < 0.35:
                self.slope_dir = 0
            elif r < 0.675:
                self.slope_dir = -1  # floor up (harder)
            else:
                self.slope_dir = +1  # floor down (easier)

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.panel_rate

    def _maybe_schedule_flat_run(self) -> None:
        self.panels_since_flat += 1
        if self.force_flat_panels_left > 0:
            return

        if self.panels_since_flat >= self.next_flat_in_panels:
            self.force_flat_panels_left = random.randint(self.flat_run_min, self.flat_run_max)
            self.panels_since_flat = 0
            self.next_flat_in_panels = random.randint(10, 16)

            # During a flat run, allow a cart after a few panels
            self.cart_ready_in = random.randint(2, 4)

    def _advance_profile_one_panel(self) -> int:
        """
        Advance floor/ceiling by one panel respecting corridor constraints.
        Returns the slope used this panel: -1, 0, +1.
        """
        H = self.screen.get_height()
        margin_top = 60
        margin_bottom = 60

        self._maybe_schedule_flat_run()

        if self.force_flat_panels_left > 0:
            slope = 0
            self.force_flat_panels_left -= 1
        else:
            slope = self.slope_dir

        # Apply slope to floor; keep ceiling roughly coupled so corridor stays sane
        new_floor = self.floor_y + slope * self.slope_per_panel

        # Keep within screen bounds
        new_floor = int(_clamp(new_floor, margin_top + self.gap, H - margin_bottom))

        # Recompute ceiling from floor and gap
        new_ceil = int(new_floor - self.gap)

        # Clamp ceiling too (this will implicitly clamp floor if needed)
        if new_ceil < margin_top:
            new_ceil = margin_top
            new_floor = new_ceil + self.gap

        self.floor_y = new_floor
        self.ceiling_y = new_ceil

        return slope

    def _maybe_spawn_tunnel_coin(self, x: int) -> list[Coin]:
        self.panels_since_coin += 1
        if self.panels_since_coin < self.next_coin_in:
            return []

        self.panels_since_coin = 0
        self.next_coin_in = random.randint(4, 7)

        center_y = (self.ceiling_y + self.floor_y) // 2
        y = center_y + random.randint(-25, 25)
        coin_x = x + self.panel_width + random.randint(110, 180)

        return [
            Coin(
                screen=self.screen,
                pos=pygame.Vector2(coin_x, y),
                radius=13,
                value=1,
                velocity=self.base_velocity,
                sprite=self.coin_sprite,
            )
        ]

    def _maybe_spawn_cart(self, x: int, slope_used: int) -> list[MineCart]:
        # Only on flat panels inside a forced flat run
        if slope_used != 0:
            return []
        if self.force_flat_panels_left <= 0:
            return []

        if self.cart_ready_in > 0:
            self.cart_ready_in -= 1
            return []

        # Prevent cart spam inside one flat run
        self.cart_ready_in = self.cart_cooldown_panels

        cart_w = 70
        cart_h = 36
        cart_x = x + self.panel_width + random.randint(160, 280)
        cart_y = self.floor_y - cart_h

        cart_vx = self.base_velocity * self.cart_speed_mult

        cart = MineCart(
            screen=self.screen,
            rect=pygame.Rect(cart_x, cart_y, cart_w, cart_h),
            velocity=cart_vx,
            sprite=self.cart_sprite,
        )

        if tunnel_field.TUNNEL_FIELD is not None:
            cart.attach_floor_field(tunnel_field.TUNNEL_FIELD)

        return [cart]

    def _spawn_slope_spikes(self, x: int, slope_used: int) -> list[RectObstacle]:
        """
        On slopes (non-flat), spawn a stalactite OR stalagmite (not both),
        keeping corridor passable.
        """
        if slope_used == 0:
            return []

        obstacles: list[RectObstacle] = []

        corridor_h = self.floor_y - self.ceiling_y
        # Keep a safe passage always
        safe_min = max(120, corridor_h - 90)  # keep at least ~120 px clear
        max_spike = max(0, corridor_h - safe_min)

        if max_spike <= 0:
            return []

        spike_w = random.randint(38, 58)
        spike_h = random.randint(int(max_spike * 0.45), int(max_spike * 0.75))
        spike_h = max(18, spike_h)

        # Slightly bias spikes opposite the slope direction for fairness
        # (when floor rises, bottom spikes are harsher; prefer top spikes)
        if slope_used < 0:
            choice = "top" if random.random() < 0.70 else "bottom"
        else:
            choice = "bottom" if random.random() < 0.70 else "top"

        sx = x + random.randint(40, self.panel_width - spike_w - 10)

        if choice == "top":
            # stalactite: grows downward from ceiling block
            sy = self.ceiling_y
            obstacles.append(
                RectObstacle(
                    self.screen,
                    pygame.Rect(sx, sy, spike_w, spike_h),
                    velocity=self.base_velocity,
                    color="gray15",
                    lethal=True,
                )
            )
        else:
            # stalagmite: grows upward from floor block
            sy = self.floor_y - spike_h
            obstacles.append(
                RectObstacle(
                    self.screen,
                    pygame.Rect(sx, sy, spike_w, spike_h),
                    velocity=self.base_velocity,
                    color="gray15",
                    lethal=True,
                )
            )

        return obstacles

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        x = W + 20 - self.overlap_px
        panel_w = self.panel_width + self.overlap_px

        slope_used = self._advance_profile_one_panel()

        # Top wall: from 0 to ceiling_y
        top_h = max(0, self.ceiling_y)
        # Bottom wall: from floor_y to bottom
        bot_h = max(0, H - self.floor_y)

        top_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, panel_w, top_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )
        bottom_wall = RectObstacle(
            self.screen,
            pygame.Rect(x, self.floor_y, panel_w, bot_h),
            velocity=self.base_velocity,
            color="slategray4",
            lethal=False,
        )

        # Floor profile for carts (only needed for cart clamping)
        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.paint_span(x0=x, x1=x + panel_w, floor_y=self.floor_y)

        obstacles = [top_wall, bottom_wall]

        # On slopes: spawn spikes (carefully)
        obstacles.extend(self._spawn_slope_spikes(x, slope_used))

        # On flats inside flat run: spawn carts
        obstacles.extend(self._maybe_spawn_cart(x, slope_used))

        coins = self._maybe_spawn_tunnel_coin(x)

        self.spawn_timer = 0.0
        return obstacles, coins
