import pygame

# ======================= #
########## TO DO ##########
# ======================= #

# Change sprite to a custom one
# Create 'spike' and 'pipe' subclasses - make 'Enemy' abstract

### Notes ###
# 'draw' and 'update' methods could have a return type (error checking)
# generalize magic numbers

# 'Enemy' class declaration and definition
class Enemy:
    def __init__(self, screen: pygame.Surface):
        # 'Enemy' objects are stored as rectangles internally
        # 'Spikes' can override this
        self.screen = screen
        self.currPos = pygame.Vector2(screen.get_width() + 20, -20)

    # NEW - hitbox integration    
    @property
    def _hitbox(self):
        return pygame.Rect(
            self.currPos.x,
            self.currPos.y,
            70,
            200
        )

    def getHitbox(self) -> pygame.Rect:
        return self._hitbox

    # Pipes move automatically
    def update(self):
        self.currPos.x -= 20
        if self.currPos.x < 0:
            self.currPos.x = self.screen.get_width() + 20

    # Display method
    def draw(self):
        pygame.draw.rect(self.screen,
                         "green",
                         (self.currPos.x, self.currPos.y, 70, 200))