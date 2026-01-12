# =========================
# FILE: src/gameplay/spawners/beams_spawner.py
# =========================
import random
import pygame
from entities import RectObstacle, Coin


def _load_coin_sprite():
    try:
        return pygame.image.load("../assets/sprites/coins/coin.png").convert_alpha()
    except Exception:
        return None


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class BeamsSpawner:
    """
    Mine support beams / frames:
    - Spacing is CONFIGURABLE via spacing_scale (and no longer "ignored")
    - Opening center moves smoothly:
        * never stays the same (no 0-step)
        * never repeats the same step twice in a row
        * prefers smaller changes over large ones (triangular distribution)
    - First beam aligns to incoming passage center; last beam aligns to outgoing center
      (provided by SectionManager through setSectionContext()).
    - Coin-light.

    Key knobs:
      - spacing_scale: 0.8 => denser beams, 1.0 => default, 1.2 => sparser
      - min_center_step: minimum vertical movement per beam (prevents "flat" sequences)
      - max_center_step: maximum vertical movement per beam (caps craziness)
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.coin_sprite = _load_coin_sprite()

        self.spawn_timer = 0.0

        # World speed
        self.base_velocity = 500.0

        # ---- spacing knob ----
        self.spacing_scale = 1.0  # 0.8 => closer beams, 1.2 => farther beams

        # Time between beams (seconds) - computed from tier * spacing_scale
        self.spawn_rate = 1.05

        # Opening size (updated by tier)
        self.opening = 280

        # Frame geometry
        self.frame_w = 90
        self.beam_thick = 40

        # Smooth movement controls (updated by tier)
        self.min_center_step = 150   # <-- tweak: minimum movement per beam
        self.max_center_step = 300   # <-- tweak: maximum movement per beam

        # Remember last step so we don't repeat it
        self._last_step: int | None = None

        # Transition anchoring
        self._entry_center_y: int | None = None
        self._exit_center_y: int | None = None
        self._remaining_in_section: float | None = None

        self._has_spawned_any = False
        self._last_center_y: int | None = None

    def setWorldSpeed(self, world_speed: float) -> None:
        self.base_velocity = float(world_speed)

    # ---- SectionManager hook ----
    def setSectionContext(
        self,
        entry_center_y: int | None,
        exit_center_y: int | None,
        remaining_time: float | None,
    ) -> None:
        self._entry_center_y = entry_center_y
        self._exit_center_y = exit_center_y
        self._remaining_in_section = remaining_time

    def reset(self) -> None:
        self.spawn_timer = 0.0
        self._has_spawned_any = False
        self._last_center_y = None
        self._last_step = None

        self._entry_center_y = None
        self._exit_center_y = None
        self._remaining_in_section = None

    def setDifficultyTier(self, tier: int) -> None:
        """
        spawn_rate is derived from tier * spacing_scale.
        If you want beams closer/farther, tweak spacing_scale, NOT spawn_rate directly.
        """
        tier = max(0, int(tier))

        # Base time between beams (seconds)
        base = 1.15 - tier * 0.03
        base = _clamp(base, 0.60, 1.20)

        self.spawn_rate = base * float(self.spacing_scale)

        # Opening shrinks with tier, but stays playable
        self.opening = max(170, 280 - tier * 8)

        # Jitter grows a bit with tier, but stays civilized
        # You can tweak the 55/95 or the growth rate to taste.
        self.max_center_step = int(_clamp(65 + tier * 1.6, 55, 95))
        self.min_center_step = int(_clamp(8 + tier * 0.2, 6, min(16, self.max_center_step)))

    def update(self, dt: float) -> None:
        self.spawn_timer += dt

    def shouldSpawn(self) -> bool:
        return self.spawn_timer >= self.spawn_rate

    def _compute_center_bounds(self) -> tuple[int, int]:
        H = self.screen.get_height()
        margin = 120
        return margin, H - margin

    def _sample_step(self) -> int:
        """
        Returns a non-zero step with:
        - magnitude in [min_center_step, max_center_step]
        - bias towards smaller magnitudes (triangular distribution)
        """
        max_step = int(self.max_center_step)
        min_step = int(min(self.min_center_step, max_step))

        # Prefer small movement, occasionally larger
        mag = int(random.triangular(min_step, max_step, min_step))
        mag = max(min_step, min(max_step, mag))

        sign = -1 if random.random() < 0.5 else 1
        step = sign * mag

        # Just in case: enforce non-zero
        if step == 0:
            step = sign * min_step if min_step > 0 else sign * 1

        return step

    def _choose_center_y(self) -> int:
        lo, hi = self._compute_center_bounds()

        # FIRST beam anchor
        if not self._has_spawned_any and self._entry_center_y is not None:
            c = int(_clamp(self._entry_center_y, lo, hi))
            self._last_center_y = c
            return c

        # LAST beam anchor (if we're likely at the last spawn of this section)
        if (
            self._exit_center_y is not None
            and self._remaining_in_section is not None
            and self._remaining_in_section <= self.spawn_rate * 1.15
        ):
            c = int(_clamp(self._exit_center_y, lo, hi))
            self._last_center_y = c
            return c

        if self._last_center_y is None:
            self._last_center_y = int((lo + hi) / 2)

        # Pick a step that:
        #  - is non-zero
        #  - is not identical to last step (prevents same-delta streaks)
        step = self._sample_step()
        tries = 0
        while self._last_step is not None and step == self._last_step:
            step = self._sample_step()
            tries += 1
            if tries > 10:
                # fallback: flip sign to force a change
                step = -self._last_step
                break

        self._last_step = step

        c = int(_clamp(self._last_center_y + step, lo, hi))
        self._last_center_y = c
        return c

    def spawn(self, tier: int):
        self.setDifficultyTier(tier)

        W = self.screen.get_width()
        H = self.screen.get_height()

        x = W + 20
        center = self._choose_center_y()

        opening_top = max(self.beam_thick, center - self.opening // 2)
        opening_bot = min(H - self.beam_thick, center + self.opening // 2)

        top = RectObstacle(
            self.screen,
            pygame.Rect(x, 0, self.frame_w, opening_top),
            velocity=self.base_velocity,
            color="sienna4",
            lethal=True,
        )
        bot = RectObstacle(
            self.screen,
            pygame.Rect(x, opening_bot, self.frame_w, H - opening_bot),
            velocity=self.base_velocity,
            color="sienna4",
            lethal=True,
        )

        obstacles = [top, bot]

        coins: list[Coin] = []
        if random.random() < 0.28:
            mid_y = (opening_top + opening_bot) // 2
            coins.append(
                Coin(
                    screen=self.screen,
                    pos=pygame.Vector2(x + self.frame_w + 90, mid_y),
                    radius=13,
                    value=1,
                    velocity=self.base_velocity,
                    sprite=self.coin_sprite,
                )
            )

        self.spawn_timer = 0.0
        self._has_spawned_any = True
        return obstacles, coins
