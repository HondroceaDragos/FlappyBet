import pygame
from debugger import Debugger


class RectObstacle:
    """
    Generic rectangular obstacle.

    lethal=False  -> solid/walkable tunnel surface (resolved by engine)
    lethal=True   -> touching kills, but can be edge-restricted with lethal_edges.

    lethal_edges can include: {"left", "right", "top", "bottom"}
    For your game: use {"left"} for the step-face so ONLY the leading edge kills.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        velocity: float,
        color="slategray4",
        lethal: bool = True,
        lethal_edges: set[str] | None = None,
        edge_margin: int = 10,
    ):
        self.screen = screen
        self.rect = rect
        self.velocity = float(velocity)
        self.color = color
        self.lethal = bool(lethal)

        # If None: default behavior
        # - lethal True -> all edges lethal
        # - lethal False -> no edges lethal
        if lethal_edges is None:
            self.lethal_edges = {"left", "right", "top", "bottom"} if self.lethal else set()
        else:
            self.lethal_edges = set(lethal_edges)

        # Thickness of edge zones in pixels for edge-based lethal checks
        self.edge_margin = int(edge_margin)

    def update(self, dt: float) -> None:
        self.rect.x -= int(self.velocity * dt)

    def shouldKill(self) -> bool:
        return self.rect.right <= 0

    def getHitbox(self) -> pygame.Rect:
        return self.rect

    def is_lethal_collision(self, player) -> bool:
        """
        Return True ONLY if the collision happens on a lethal edge zone.
        This prevents the right edge of a step-face from killing after you passed it.
        """
        if not self.lethal:
            return False

        # If all edges are lethal, you can just treat any overlap as lethal
        if self.lethal_edges == {"left", "right", "top", "bottom"}:
            return True

        center, radius = player.getHitbox()

        # Overlap already confirmed by caller; now decide whether it's on a lethal edge.
        m = self.edge_margin

        # Define thin edge zones
        if "left" in self.lethal_edges:
            left_zone = pygame.Rect(self.rect.left, self.rect.top, m, self.rect.height)
            if self._circle_rect_overlap(center, radius, left_zone):
                return True

        if "right" in self.lethal_edges:
            right_zone = pygame.Rect(self.rect.right - m, self.rect.top, m, self.rect.height)
            if self._circle_rect_overlap(center, radius, right_zone):
                return True

        if "top" in self.lethal_edges:
            top_zone = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, m)
            if self._circle_rect_overlap(center, radius, top_zone):
                return True

        if "bottom" in self.lethal_edges:
            bottom_zone = pygame.Rect(self.rect.left, self.rect.bottom - m, self.rect.width, m)
            if self._circle_rect_overlap(center, radius, bottom_zone):
                return True

        return False

    @staticmethod
    def _circle_rect_overlap(center: pygame.Vector2, radius: float, rect: pygame.Rect) -> bool:
        cx, cy = center.x, center.y
        closest_x = max(rect.left, min(cx, rect.right))
        closest_y = max(rect.top, min(cy, rect.bottom))
        dx = cx - closest_x
        dy = cy - closest_y
        return (dx * dx + dy * dy) < (radius * radius)

    def draw(self) -> None:
        pygame.draw.rect(self.screen, self.color, self.rect)

        if Debugger.HITBOXES:
            outline = "green" if not self.lethal else "red"
            pygame.draw.rect(self.screen, outline, self.rect, 2)

            # If edge-based lethal, visualize edge zones (optional but helpful)
            if self.lethal and self.lethal_edges != {"left", "right", "top", "bottom"}:
                m = self.edge_margin
                if "left" in self.lethal_edges:
                    pygame.draw.rect(self.screen, "red", (self.rect.left, self.rect.top, m, self.rect.height), 1)
                if "right" in self.lethal_edges:
                    pygame.draw.rect(self.screen, "red", (self.rect.right - m, self.rect.top, m, self.rect.height), 1)
                if "top" in self.lethal_edges:
                    pygame.draw.rect(self.screen, "red", (self.rect.left, self.rect.top, self.rect.width, m), 1)
                if "bottom" in self.lethal_edges:
                    pygame.draw.rect(self.screen, "red", (self.rect.left, self.rect.bottom - m, self.rect.width, m), 1)
