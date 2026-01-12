# =========================
# FILE: src/gameplay/section_manager.py
# (HazardPatch removed; section-level lava is handled by checking current section)
# =========================
import random
import pygame

from gameplay.spawners.spikes_spawner import SpikesSpawner
from gameplay.spawners.tunnel_spawner import TunnelSpawner
from gameplay.spawners.beams_spawner import BeamsSpawner


class SectionManager:
    """
    Cycles sections. Difficulty is fixed during a section.
    Difficulty for a section type increases only after that section is completed.

    NOTE:
      We do NOT spawn lava objects here.
      "Spikes floor is lava" should be implemented as a section-level rule:
        if current section == "spikes" and player touches floor band -> die.
      This makes lava start instantly and stop exactly when section changes.
    """

    SECTION_TYPES = ["spikes", "tunnel", "beams"]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.spawners = {
            "spikes": SpikesSpawner(screen),
            "tunnel": TunnelSpawner(screen),
            "beams": BeamsSpawner(screen),
        }

        # tier per section type
        self.tier: dict[str, int] = {k: 0 for k in self.SECTION_TYPES}

        self.current_type: str = "spikes"
        self.current_tier: int = 0

        self.section_time = 0.0
        self.section_duration = 10.0  # seconds

        self.transition_timer = 0.0
        self.transition_duration = 0.6   # seconds, tweak

    def reset(self) -> None:
        self.tier = {k: 0 for k in self.SECTION_TYPES}
        self.current_type = "spikes"
        self.current_tier = self.tier[self.current_type]
        self.section_time = 0.0
        self.section_duration = 10.0
        self.transition_timer = 0.0

        for sp in self.spawners.values():
            sp.reset()

    def _choose_next_section(self) -> str:
        # Avoid repeating the same section back-to-back
        options = [t for t in self.SECTION_TYPES if t != self.current_type]
        return random.choice(options)

    def _compute_duration(self) -> float:
        # Later tiers: slightly longer sections, but not endless
        return 9.0 + min(6.0, self.current_tier * 0.4)

    def update(self, dt: float) -> None:
        self.section_time += dt
        self.transition_timer = self.transition_duration

        spawner = self.spawners[self.current_type]
        spawner.update(dt)

        if self.transition_timer > 0.0:
            self.transition_timer = max(0.0, self.transition_timer - dt)

        if self.section_time >= self.section_duration:
            # Complete current section -> increase its tier for next time
            self.tier[self.current_type] += 1

            # Switch section
            self.current_type = self._choose_next_section()
            self.current_tier = self.tier[self.current_type]

            self.section_time = 0.0
            self.section_duration = self._compute_duration()

            # Reset the new spawner so timing feels clean
            self.spawners[self.current_type].reset()

    def maybe_spawn(self, hazard_intensity: float = 0.0, world_speed: float = 520.0):
        spawner = self.spawners[self.current_type]

        if hasattr(spawner, "setWorldSpeed"):
            spawner.setWorldSpeed(world_speed)

        if hasattr(spawner, "setHazardIntensity"):
            spawner.setHazardIntensity(hazard_intensity)

        remaining = max(0.0, self.section_duration - self.section_time)

        # A decent “passage center” definition:
        H = self.screen.get_height()
        entry_center = getattr(self, "last_passage_center_y", H // 2)

        # Predict next section’s entry center. For now: same as current.
        # (If you want it smarter: set this when switching sections.)
        exit_center = entry_center

        if hasattr(spawner, "setSectionContext"):
            spawner.setSectionContext(entry_center, exit_center, remaining)

        if spawner.shouldSpawn():
            return spawner.spawn(self.current_tier)
        
        if self.transition_timer > 0.0:
            return [], []

        return [], []

    # -----------------------
    # Section info / helpers
    # -----------------------
    def getSectionName(self) -> str:
        return self.current_type

    def getTier(self) -> int:
        return self.current_tier

    def isSpikes(self) -> bool:
        return self.current_type == "spikes"

    def getSpikesLavaHeight(self) -> int:
        """
        Used by GameInProgressState to apply 'floor is lava' only during spikes.
        """
        sp = self.spawners.get("spikes")
        return int(getattr(sp, "lava_height", 0))
