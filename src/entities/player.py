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


# Helper function - will add animations later
def loadPlayerSprites(radius: float):
    sprites = {}

    idleSprite = pygame.image.load(
        "../assets/sprites/playerSprites/idleSprite.png"
    ).convert_alpha()
    idleSprite = pygame.transform.smoothscale(
        idleSprite, (int(2 * radius), int(2 * radius))
    )

    flySprite = pygame.image.load(
        "../assets/sprites/playerSprites/flySprite.png"
    ).convert_alpha()
    flySprite = pygame.transform.smoothscale(
        flySprite, (int(2 * radius), int(2 * radius))
    )

    dropSprite = pygame.image.load(
        "../assets/sprites/playerSprites/dropSprite.png"
    ).convert_alpha()
    dropSprite = pygame.transform.smoothscale(
        dropSprite, (int(2 * radius), int(2 * radius))
    )

    sprites["idleSprite"] = idleSprite
    sprites["flySprite"] = flySprite
    sprites["dropSprite"] = dropSprite

    return sprites


# 'Player' class declaration and definition
class Player:
    # Fields specifically declared for access modifiers (private)
    _radius: float = 3.0
    _currentSprite: str = None

    def __init__(
        self,
        screen: pygame.Surface,
        currPos: pygame.Vector2 = None,
        radius: float = 3.0,
        velocity: pygame.Vector2 = pygame.Vector2(0, 0),
    ):
        # 'Player' object is stored internally as a circle
        self.screen = screen
        self._radius = radius
        self.velocity = velocity

        # Load sprites
        self.sprites = loadPlayerSprites(self._radius)
        self._currentSprite = self.sprites["idleSprite"]

        # Default state
        self.jumpPressed = False
        self.state = "IDLE"

        # Spawn position
        if currPos is None:
            self.currPos = pygame.Vector2(
                screen.get_width() / 2, screen.get_height() / 2
            )
        else:
            self.currPos = currPos

    # NEW - hitbox integration
    @property
    def _hitbox(self):
        return (self.currPos, self._radius)

    def getHitbox(self):
        return self._hitbox

    # Change sprites
    def changeSprite(self, name: str) -> None:
        self._currentSprite = self.sprites[name]

    # Core of animation engine
    def decideState(self) -> None:
        # Player is on ground
        if self.currPos.y + self._radius >= self.screen.get_height():
            self.state = "IDLE"
        else:
            # Player is flying
            if self.velocity.y < 0:
                self.state = "FLYING"
            # VERY IMPORTANT FOR GAME FEEL - if 'jump' is pressed
            # the flying sprite is shown - makes it feel like the bird
            # is trying to fly harder
            elif (
                self.jumpPressed
                and self.currPos.y + self._radius < self.screen.get_height()
            ):
                self.state = "FLYING"
            # Player is dropping
            elif self.velocity.y > 0:
                self.state = "FALLING"

    # Animation engine - in-between frames TBA
    def animatePlayer(self) -> None:
        match self.state:
            case "IDLE":
                self.changeSprite("idleSprite")

            case "FLYING":
                self.changeSprite("flySprite")

            case "FALLING":
                self.changeSprite("dropSprite")

    # Display method
    def draw(self) -> None:
        # Draw only the player - no hitbox
        rect = self._currentSprite.get_rect(center=self.currPos)
        self.screen.blit(self._currentSprite, rect)

        # Player hitbox
        pygame.draw.circle(self.screen, "red", self.currPos, self._radius, 2)
