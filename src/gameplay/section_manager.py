# =========================
# NEW FILE: src/gameplay/section_manager.py
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

        # mild variety
        self._next_pool = ["spikes", "tunnel", "beams"]

    def reset(self) -> None:
        self.tier = {k: 0 for k in self.SECTION_TYPES}
        self.current_type = "spikes"
        self.current_tier = self.tier[self.current_type]
        self.section_time = 0.0
        self.section_duration = 10.0

        for sp in self.spawners.values():
            sp.reset()

    def _choose_next_section(self) -> str:
        # avoid same section twice too often
        options = [t for t in self.SECTION_TYPES if t != self.current_type]
        return random.choice(options)

    def _compute_duration(self) -> float:
        # later tiers: slightly longer sections, but not endless
        return 9.0 + min(6.0, self.current_tier * 0.4)

    def update(self, dt: float) -> None:
        self.section_time += dt

        spawner = self.spawners[self.current_type]
        spawner.update(dt)

        if self.section_time >= self.section_duration:
            # complete current section -> increase its tier for next time
            self.tier[self.current_type] += 1

            # switch section
            self.current_type = self._choose_next_section()
            self.current_tier = self.tier[self.current_type]

            self.section_time = 0.0
            self.section_duration = self._compute_duration()

            # reset the new spawner so timing feels clean
            self.spawners[self.current_type].reset()

    def maybe_spawn(self, hazard_intensity: float = 0.0):
        spawner = self.spawners[self.current_type]

        # Only spikes spawner uses hazard_intensity for lava/ceiling patches
        if self.current_type == "spikes" and hasattr(spawner, "setHazardIntensity"):
            spawner.setHazardIntensity(hazard_intensity)

        if spawner.shouldSpawn():
            return spawner.spawn(self.current_tier)

        return [], []

    def getSectionName(self) -> str:
        return self.current_type

    def getTier(self) -> int:
        return self.current_tier
