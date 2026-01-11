import random
import pygame

from entities import Pipe
from entities import Coin
from entities import HazardPatch


def _load_pipe_sprites() -> list[pygame.Surface]:
    v1 = pygame.image.load("../assets/sprites/pipeSprites/pipeVariant1.png").convert_alpha()
    v2 = pygame.image.load("../assets/sprites/pipeSprites/pipeVariant2.png").convert_alpha()
    return [v1, v2]


def _choose(sprites: list[pygame.Surface]) -> pygame.Surface:
    return random.choice(sprites)


def _load_coin_sprite() -> pygame.Surface | None:
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _sample_spike_height(
    min_h: int,
    max_h: int,
    p_small: float = 0.12,
    p_large: float = 0.12,
) -> int:
    """
    3-bucket distribution:
      - small spikes (rare): biased toward min_h
      - middle spikes (common): biased toward middle
      - large spikes (rare): biased toward max_h

    p_small + p_large must be <= 1.0
    """
    min_h = int(min_h)
    max_h = int(max_h)
    if max_h <= min_h:
        return min_h

    p_small = float(_clamp(p_small, 0.0, 0.45))
    p_large = float(_clamp(p_large, 0.0, 0.45))
    if p_small + p_large > 0.95:
        # keep middle bucket non-empty
        s = (p_small + p_large) / 0.95
        p_small /= s
        p_large /= s

    r = random.random()
    mid = (min_h + max_h) / 2

    if r < p_small:
        # small: bias low
        h = random.triangular(min_h, max_h, min_h)
    elif r > 1.0 - p_large:
        # large: bias high
        h = random.triangular(min_h, max_h, max_h)
    else:
        # middle: strong bias to mid
        h = random.triangular(min_h, max_h, mid)

    return int(_clamp(h, min_h, max_h))


class Fireball:
    """
    Lethal hazard for spike sections.

    - Moves left at world speed.
    - Erupts from UNDER the lava to a peak height (peak_y), then returns under lava.
    - peak_y is a FIELD, rolled at spawn and optionally rerolled each cycle.
    - Equiprobable heights by default (uniform).
    """

    def __init__(
        self,
        screen: pygame.Surface,
        x: float,
        velocity: float,
        lava_top_y: float,
        radius: int = 16,
        period: float = 1.9,
        under_lava: float = 70.0,
        # preferred interface: pick peak between "just above lava" and "near ceiling"
        peak_min_above_lava: float = 24.0,
        peak_max_y: float | None = None,
        uniform_peak: bool = True,
        color: str = "orange",
        reroll_each_cycle: bool = False,
        # backwards-compat aliases:
        min_peak_y: float | None = None,
        max_peak_y: float | None = None,
    ):
        self.screen = screen
        self.velocity = float(velocity)
        self.radius = int(radius)
        self.color = color
        self.lethal = True

        self.lava_top_y = float(lava_top_y)
        self.rest_y = self.lava_top_y + float(under_lava)
        self.x = float(x)
        self.y = self.rest_y

        self.period = max(0.7, float(period))
        self._phase = random.random()

        self.uniform_peak = bool(uniform_peak)
        self.reroll_each_cycle = bool(reroll_each_cycle)

        # Resolve peak range:
        # If caller provided absolute min/max peak y, use those.
        if min_peak_y is not None or max_peak_y is not None:
            # Defaults if one missing
            if min_peak_y is None:
                min_peak_y = self.lava_top_y - float(peak_min_above_lava)
            if max_peak_y is None:
                max_peak_y = 70.0
            self.peak_min_y = float(min_peak_y)
            self.peak_max_y = float(max_peak_y)
        else:
            # Use the "above lava" min + an absolute max near ceiling
            self.peak_min_y = self.lava_top_y - float(peak_min_above_lava)
            if peak_max_y is None:
                peak_max_y = 70.0
            self.peak_max_y = float(peak_max_y)

        # Ensure range is valid: peak_max_y should be higher (smaller y)
        if self.peak_max_y > self.peak_min_y:
            self.peak_max_y, self.peak_min_y = self.peak_min_y, self.peak_max_y

        self.peak_y = self._roll_peak_y()

    def _roll_peak_y(self) -> float:
        lo = self.peak_max_y  # higher (smaller y)
        hi = self.peak_min_y  # lower (larger y)
        if self.uniform_peak:
            return float(random.uniform(lo, hi))
        return float(random.triangular(lo, hi, (lo + hi) / 2))

    def update(self, dt: float) -> None:
        self.x -= self.velocity * dt

        prev = self._phase
        self._phase = (self._phase + dt / self.period) % 1.0
        if self.reroll_each_cycle and self._phase < prev:
            self.peak_y = self._roll_peak_y()

        t = self._phase
        jump = 4.0 * t * (1.0 - t)
        self.y = self.rest_y + (self.peak_y - self.rest_y) * jump

    def shouldKill(self) -> bool:
        return self.x + self.radius <= 0

    def getHitbox(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )

    def draw(self) -> None:
        pygame.draw.circle(self.screen, self.color, (int(self.x), int(self.y)), self.radius)


class SpikesSpawner:
    """
    Spikes section:
    - fixed difficulty per section (tier)
    - spikes have heavy-tailed random height distribution
    - coins spawn only every few obstacles
    - THE ENTIRE FLOOR IS ALWAYS LAVA during spike sections
    - hazards are FIREBALLS (move left at world speed, erupt from lava)
    - fireballs never spawn on/adjacent-to a large spike (same tick, ±1 tick)
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
        self.next_coin_in = random.randint(3, 6)

        # Spike randomness
        self.big_spike_chance = 0.14
        self.large_spike_threshold_ratio = 0.78

        # Floor lava
        self.lava_height = 34

        # Fireballs tuning
        # Make them more common even at lowest difficulty:
        self.fireball_base_prob = 0.38         # was ~0.28; this is noticeably more frequent
        self.fireball_min_gap_obstacles = 3    # was 4; allows earlier spawns
        self.obstacles_since_fireball = 999

        # Exclusion window around large spikes: forbid fireballs on large spike spawn
        # and on the next spawn. Also forbids one spawn "after".
        self.large_spike_exclusion = 0

        # hazard_intensity kept for compatibility (not used for lava anymore)
        self.hazard_intensity = 0.0

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self.curr_pattern = random.choice(self.spawn_patterns)
        self.pattern_idx = 0

        self.obstacles_since_coin = 0
        self.next_coin_in = random.randint(3, 6)

        self.obstacles_since_fireball = 999
        self.large_spike_exclusion = 0

    def setDifficultyTier(self, tier: int) -> None:
        tier = max(0, int(tier))
        self.base_velocity = 500.0 + tier * 35.0
        self.spawn_rate = max(0.55, 0.85 - tier * 0.03)

        # Slightly more big spikes later (cap)
        self.big_spike_chance = float(_clamp(0.12 + 0.01 * min(tier, 6), 0.12, 0.18))

        # Fireballs: modest scaling, but already decent at tier 0
        # - probability rises a bit with tier
        self.fireball_base_prob = float(_clamp(0.38 + 0.02 * min(tier, 5), 0.38, 0.50))
        # - minimum gap shrinks slightly with tier (but never spammy)
        self.fireball_min_gap_obstacles = max(2, 3 - tier // 7)

    def setHazardIntensity(self, hazard_intensity: float) -> None:
        self.hazard_intensity = float(_clamp(hazard_intensity, 0.0, 1.0))

    def update(self, dt: float) -> None:
        self.spawn_timer += dt

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.spawn_rate

    def _next_orientation(self) -> str:
        orientation = self.curr_pattern[self.pattern_idx]
        self.pattern_idx += 1
        if self.pattern_idx >= len(self.curr_pattern):
            self.curr_pattern = random.choice(self.spawn_patterns)
            self.pattern_idx = 0
        return orientation

    def _spawn_floor_lava(self, spike_x: int) -> HazardPatch:
        """
        Always-on lava: spawn long overlapping strips so the bottom is continuously lethal.
        """
        W = self.screen.get_width()
        H = self.screen.get_height()

        strip_w = int(W * 1.35)
        strip_h = int(self.lava_height)

        strip_x = int(spike_x - (W * 0.15))
        strip_y = int(H - strip_h)

        return HazardPatch(
            screen=self.screen,
            rect=pygame.Rect(strip_x, strip_y, strip_w, strip_h),
            velocity=self.base_velocity,
            color="orangered3",
        )

    def _maybe_spawn_fireball(self, spike_x: int, is_large_spike: bool) -> list[Fireball]:
        """
        Fireballs:
          - more common even at tier 0
          - never on large spike spawn, and never immediately after a large spike
          - move at world speed
          - erupt from under lava to a randomized peak height
        """
        # Tick exclusion window down once per spawn tick
        if self.large_spike_exclusion > 0:
            self.large_spike_exclusion -= 1

        # If this is a large spike: forbid now + next tick
        if is_large_spike:
            self.large_spike_exclusion = max(self.large_spike_exclusion, 1)
            return []

        # If we're in exclusion window (right after a large spike), forbid
        if self.large_spike_exclusion > 0:
            return []

        # Throttle
        self.obstacles_since_fireball += 1
        if self.obstacles_since_fireball < self.fireball_min_gap_obstacles:
            return []

        # Probability (higher even at lowest tier)
        if random.random() > self.fireball_base_prob:
            return []

        self.obstacles_since_fireball = 0

        W = self.screen.get_width()
        H = self.screen.get_height()

        lava_top = H - self.lava_height

        # Spawn after the spike so it reads as a follow-up threat
        fx = spike_x + Pipe.Proportions.WIDTH.value + random.randint(150, 320)

        # Configure peak range:
        # min peak is "a bit above lava"
        peak_min_above_lava = random.uniform(18.0, 34.0)  # slightly varied minimum hop

        # max peak is "a little over halfway screen" (above midpoint -> smaller y)
        # Example: 0.45H. Clamp so it's always above min peak.
        peak_max_y = int(H * 0.45)
        peak_min_y_abs = lava_top - peak_min_above_lava
        peak_max_y = int(_clamp(peak_max_y, 70, peak_min_y_abs - 25))

        # Slower eruption cycle
        period = random.uniform(1.6, 2.35)

        # Slightly varied under-lava depth so timing feels organic
        under_lava = random.uniform(55, 90)

        radius = random.randint(14, 18)

        return [
            Fireball(
                screen=self.screen,
                x=fx,
                velocity=self.base_velocity,
                lava_top_y=lava_top,
                radius=radius,
                period=period,
                under_lava=under_lava,
                peak_min_above_lava=peak_min_above_lava,
                peak_max_y=peak_max_y,
                uniform_peak=True,          # equiprobable height range
                reroll_each_cycle=True,     # new peak each eruption
                color="orange",
            )
        ]

    def spawn(self, tier: int) -> tuple[list, list[Coin]]:
        self.setDifficultyTier(tier)

        orientation = self._next_orientation()

        W = self.screen.get_width()
        H = self.screen.get_height()

        spike_x = W + 20

        # Spike height range: sane limits
        base_h = Pipe.Proportions.BASE_HEIGHT.value
        min_h = max(65, int(base_h * 0.68))
        max_h = min(int(H * 0.58), int(base_h * 2.35))

        spike_h = _sample_spike_height(min_h, max_h, p_small=0.10, p_large=0.12)

        # Large spike detection
        large_cut = int(min_h + self.large_spike_threshold_ratio * (max_h - min_h))
        is_large_spike = spike_h >= large_cut

        # Place spike
        if orientation == "top":
            spike_y = random.randint(-self.edge, 0)
        else:
            spike_y = random.randint(H - spike_h, H - self.edge)

        pipe = Pipe(
            screen=self.screen,
            currPos=pygame.Vector2(spike_x, spike_y),
            velocity=self.base_velocity,
            orientation=orientation,
            sprite=_choose(self.sprites),
            height=spike_h,
        )

        obstacles: list = []

        # Always-on floor lava for spike sections
        obstacles.append(self._spawn_floor_lava(spike_x))

        # The spike itself
        obstacles.append(pipe)

        # Fireballs (more common, but excluded near large spikes)
        obstacles.extend(self._maybe_spawn_fireball(spike_x, is_large_spike))

        # Coins
        coins: list[Coin] = []
        self.obstacles_since_coin += 1
        if self.obstacles_since_coin >= self.next_coin_in:
            self.obstacles_since_coin = 0
            self.next_coin_in = random.randint(3, 6)

            coin_x = spike_x + Pipe.Proportions.WIDTH.value + random.randint(70, 140)

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

        self.spawn_timer = 0.0
        return obstacles, coins
