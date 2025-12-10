import pygame

# ======================= #
########## TO DO ##########
# ======================= #

# Add sound effects when pressing space (could be stored here)
# Change sprite to a custom one
# Add getter for '_radius'
# Add player score

### Notes ###
# 'draw' method could have a return type (error checking)

# 'Player' class declaration and definition
class Player:
    # Fields specifically declared for access modifiers (private)
    _radius: float = 3.0
    def __init__(self, screen: pygame.Surface,
                 currPos: pygame.Vector2 = None,
                 radius: float = 3.0,
                 velocity: pygame.Vector2 = pygame.Vector2(0, 0)):
        # 'Player' object is stored internally as a circle
        self.screen = screen
        self._radius = radius
        self.velocity = velocity

        # Spawn position
        if currPos is None:
            self.currPos = pygame.Vector2(
                screen.get_width() / 2,
                screen.get_height() / 2
                )
        else:
            self.currPos = currPos

        # Sprite loading
        self.image = pygame.image.load("../assets/sprites/player.png").convert_alpha()
        self.image = pygame.transform.smoothscale(self.image,
                                                  (int(radius*2),
                                                   int(radius*2)))

    # Display method
    def draw(self) -> None:
        # Draw only the player - no hitbox
        rect = self.image.get_rect(center=self.currPos)
        self.screen.blit(self.image, rect)
        pygame.draw.circle(self.screen,
                           "red",
                           self.currPos,
                           self._radius,
                           2)