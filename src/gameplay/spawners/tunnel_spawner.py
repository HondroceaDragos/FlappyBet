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
    - Player auto-climbs via solid resolution.
    - Flat stretches for carts.
    - On slopes: generate spike BUNDLES that alternate top/bottom and include forced gaps,
      preventing impassable clustering.
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
        self.min_corridor = 175

        self.floor_y = int(H * 0.70)
        self.ceiling_y = int(H * 0.25)

        # Slope control
        self.slope_per_panel = 10
        self.slope_dir = 0

        self.target_timer = 0.0
        self.target_interval = 0.85

        # Flat-run scheduling (for carts)
        self.force_flat_panels_left = 0
        self.flat_run_min = 6
        self.flat_run_max = 10
        self.next_flat_in_panels = random.randint(10, 16)
        self.panels_since_flat = 0

        # Carts
        self.cart_sprite = _load_cart_sprite()
        self.cart_speed_mult = 1.30
        self.cart_cooldown_panels = 7
        self.cart_ready_in = 0

        # Coins
        self.coin_sprite = _load_coin_sprite()
        self.panels_since_coin = 0
        self.next_coin_in = random.randint(4, 7)

        # -------------------------
        # Slope spike pattern state
        # -------------------------
        self._spike_mode = "gap"             # "bundle" or "gap"
        self._bundle_left = 0                # panels remaining in current bundle
        self._gap_left = random.randint(2, 4)
        self._bundle_side = random.choice(["top", "bottom"])  # side for next bundle
        self._bundle_target_h = 0            # base height used within bundle (keeps it readable)
        self._bundle_target_w = 0            # base width used within bundle

        # Tuning knobs
        self.bundle_len_min = 2
        self.bundle_len_max = 5
        self.gap_len_min = 1
        self.gap_len_max = 2

        # Corridor safety:
        # We guarantee at least this much free vertical passage when spikes exist.
        self.safe_passage_min = 100

        # Floor field for carts
        if tunnel_field.TUNNEL_FIELD is None:
            tunnel_field.TUNNEL_FIELD = tunnel_field.TunnelField(
                screen_width=self.screen.get_width(),
                default_floor_y=self.screen.get_height(),
                sample_step=4,
            )

    def setWorldSpeed(self, world_speed: float) -> None:
        self.base_velocity = float(world_speed)

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

        # spike pattern reset
        self._spike_mode = "gap"
        self._bundle_left = 0
        self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)
        self._bundle_side = random.choice(["top", "bottom"])
        self._bundle_target_h = 0
        self._bundle_target_w = 0

        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.reset()

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))

        self.gap = max(self.min_corridor, 240 - tier * 6)

        self.panel_rate = max(0.16, 0.22 - tier * 0.003)
        self.slope_per_panel = int(_clamp(10 + tier * 0.3, 10, 14))

        self.flat_run_min = max(5, 6 - tier // 10)
        self.flat_run_max = max(self.flat_run_min, 10 - tier // 8)

        self.cart_cooldown_panels = max(5, 7 - tier // 8)

        # Slightly tighter pattern later but still safe
        self.bundle_len_max = int(_clamp(4 + tier * 0.05, 4, 5))
        self.gap_len_min = max(2, 2 - tier // 20)  # basically stays 2
        self.safe_passage_min = max(130, 140 - tier // 12)

    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        self.target_timer += dt

        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.update(dt, self.base_velocity)

        if self.force_flat_panels_left <= 0 and self.target_timer >= self.target_interval:
            self.target_timer = 0.0
            r = random.random()
            if r < 0.35:
                self.slope_dir = 0
            elif r < 0.675:
                self.slope_dir = -1
            else:
                self.slope_dir = +1

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
            self.cart_ready_in = random.randint(2, 4)

    def _advance_profile_one_panel(self) -> int:
        H = self.screen.get_height()
        margin_top = 60
        margin_bottom = 60

        self._maybe_schedule_flat_run()

        if self.force_flat_panels_left > 0:
            slope = 0
            self.force_flat_panels_left -= 1
        else:
            slope = self.slope_dir

        new_floor = self.floor_y + slope * self.slope_per_panel
        new_floor = int(_clamp(new_floor, margin_top + self.gap, H - margin_bottom))

        new_ceil = int(new_floor - self.gap)
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
        if slope_used != 0:
            return []
        if self.force_flat_panels_left <= 0:
            return []

        if self.cart_ready_in > 0:
            self.cart_ready_in -= 1
            return []

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

    # -------------------------
    # New slope spike system
    # -------------------------
    def _begin_new_bundle(self) -> None:
        self._spike_mode = "bundle"
        self._bundle_left = random.randint(self.bundle_len_min, self.bundle_len_max)

        # Alternate side every bundle
        self._bundle_side = "bottom" if self._bundle_side == "top" else "top"

        # Pick a readable width/height for this bundle
        corridor_h = self.floor_y - self.ceiling_y
        max_spike = max(0, corridor_h - self.safe_passage_min)

        if max_spike <= 20:
            # corridor too tight -> effectively skip by forcing a gap
            self._spike_mode = "gap"
            self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)
            self._bundle_left = 0
            return

        self._bundle_target_w = random.randint(38, 56)

        # Mostly middle, few small, few large, but never near "impassable"
        lo = int(max_spike * 0.35)
        hi = int(max_spike * 0.70)
        lo = max(18, lo)
        hi = max(lo, hi)

        r = random.random()
        if r < 0.12:
            self._bundle_target_h = random.randint(18, max(18, int(lo * 0.9)))
        elif r > 0.88:
            self._bundle_target_h = random.randint(max(lo, int(hi * 0.85)), hi)
        else:
            self._bundle_target_h = random.randint(lo, hi)

        self._bundle_target_h = int(_clamp(self._bundle_target_h, 18, max_spike))

    def _spawn_slope_spikes(self, x: int, slope_used: int) -> list[RectObstacle]:
        """
        Only on slopes:
        - produce alternating TOP/BOTTOM spike bundles
        - enforce gaps between bundles
        - within a bundle: 1 spike per panel, positioned with jitter, height is stable-ish
        """
        if slope_used == 0:
            # On flats: don't generate slope spikes, and also reset to a gap
            # so we don't resume a bundle immediately after a cart-flat.
            self._spike_mode = "gap"
            self._bundle_left = 0
            self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)
            return []

        # If corridor is very tight, force gaps more often
        corridor_h = self.floor_y - self.ceiling_y
        if corridor_h < self.safe_passage_min + 25:
            self._spike_mode = "gap"
            self._bundle_left = 0
            self._gap_left = max(self._gap_left, 3)

        # Advance pattern state
        if self._spike_mode == "gap":
            self._gap_left -= 1
            if self._gap_left <= 0:
                self._begin_new_bundle()
            return []

        # bundle mode
        if self._bundle_left <= 0:
            self._spike_mode = "gap"
            self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)
            return []

        # Corridor safety re-check
        max_spike = max(0, corridor_h - self.safe_passage_min)
        if max_spike <= 20:
            self._bundle_left = 0
            self._spike_mode = "gap"
            self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)
            return []

        spike_w = self._bundle_target_w
        spike_h = int(_clamp(self._bundle_target_h + random.randint(-10, 10), 18, max_spike))

        # Position within panel, but keep jitter limited so bundle is readable
        sx = x + random.randint(48, max(49, self.panel_width - spike_w - 14))

        obstacles: list[RectObstacle] = []
        if self._bundle_side == "top":
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

        self._bundle_left -= 1
        if self._bundle_left <= 0:
            self._spike_mode = "gap"
            self._gap_left = random.randint(self.gap_len_min, self.gap_len_max)

        return obstacles

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        x = W + 20 - self.overlap_px
        panel_w = self.panel_width + self.overlap_px

        slope_used = self._advance_profile_one_panel()

        top_h = max(0, self.ceiling_y)
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

        if tunnel_field.TUNNEL_FIELD is not None:
            tunnel_field.TUNNEL_FIELD.paint_span(x0=x, x1=x + panel_w, floor_y=self.floor_y)

        obstacles = [top_wall, bottom_wall]

        # New: alternating spike bundles (only on slopes)
        obstacles.extend(self._spawn_slope_spikes(x, slope_used))

        # Carts on flat stretches
        obstacles.extend(self._maybe_spawn_cart(x, slope_used))

        coins = self._maybe_spawn_tunnel_coin(x)

        self.spawn_timer = 0.0
        return obstacles, coins
