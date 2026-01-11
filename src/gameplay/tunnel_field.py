from __future__ import annotations
import math


class TunnelField:
    """
    Continuous 1D floor profile across screen X (sampled heightmap).
    """

    def __init__(self, screen_width: int, default_floor_y: int, sample_step: int = 4):
        self.screen_width = int(screen_width)
        self.default_floor_y = float(default_floor_y)

        self.sample_step = max(1, int(sample_step))
        self.sample_count = int(math.ceil(self.screen_width / self.sample_step)) + 16

        self._heights = [self.default_floor_y] * self.sample_count
        self._last_height = self.default_floor_y
        self._accum_shift_px = 0.0

    def reset(self) -> None:
        self._heights = [self.default_floor_y] * self.sample_count
        self._last_height = self.default_floor_y
        self._accum_shift_px = 0.0

    def update(self, dt: float, velocity: float) -> None:
        dx = float(velocity) * float(dt)
        if dx <= 0:
            return

        self._accum_shift_px += dx

        while self._accum_shift_px >= self.sample_step:
            self._accum_shift_px -= self.sample_step
            self._heights.pop(0)
            self._heights.append(self._last_height)

    def paint_span(self, x0: float, x1: float, floor_y: float) -> None:
        floor_y = float(floor_y)
        self._last_height = floor_y

        if x1 < x0:
            x0, x1 = x1, x0

        x0 = max(0.0, x0)
        x1 = min(float(self.screen_width + 400), x1)

        if x1 <= 0:
            return

        i0 = int(x0 / self.sample_step)
        i1 = int(x1 / self.sample_step)

        if i1 < 0 or i0 >= len(self._heights):
            return

        i0 = max(0, i0)
        i1 = min(len(self._heights) - 1, i1)

        for i in range(i0, i1 + 1):
            self._heights[i] = floor_y

    def floor_y_at(self, x: float) -> float:
        idx = int(float(x) / self.sample_step)
        if idx < 0:
            idx = 0
        if idx >= len(self._heights):
            idx = len(self._heights) - 1
        return self._heights[idx]


# 🔑 THIS IS WHAT YOU WERE MISSING
TUNNEL_FIELD: TunnelField | None = None
