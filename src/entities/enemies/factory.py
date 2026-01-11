import pygame
from ._pipe import Pipe
import random


# helper function for loading variants
def loadSprites():
    sprites = []

    variantOne = pygame.image.load(
        "../assets/sprites/pipeSprites/pipeVariant1.png"
    ).convert_alpha()

    variantTwo = pygame.image.load(
        "../assets/sprites/pipeSprites/pipeVariant2.png"
    ).convert_alpha()

    sprites.append(variantOne)
    sprites.append(variantTwo)

    return sprites


# Choose one variant for the pipe
def chooseSprite(sprites):
    idx = random.randint(0, len(sprites) - 1)

    return sprites[idx]


# 'PipeFactory' class declaration and definition
class PipeFactory:
    # Spawn patterns to avoid weird pseudo-randomness
    spawnPatterns = [
        ["top", "bottom"],
        ["bottom", "top", "bottom", "top"],
        ["top", "bottom", "top"],
        ["bottom", "top"],
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.dftVelocity = 500.0

        self.dftSpawnRate = 0.8
        # First spawn is always faster - game start
        self.dtSpawn = 0.5

        # Maximum distance from top or bot
        self.edge = int(self.screen.get_height() * 0.05)

        # Choose one of the patterns
        self.currPattern = random.choice(self.spawnPatterns)
        self.patternIdx = 0

        self.sprites = loadSprites()

    # Height function
    def _computePipeHeight(self, passed_count: int) -> int:
        base = Pipe.Proportions.BASE_HEIGHT.value

        growth_per = 10
        max_extra = int(self.screen.get_height() * 0.55)

        extra = min(max_extra, passed_count * growth_per)
        return base + extra

    # Add elapsed time
    def update(self, dt: float) -> None:
        self.dtSpawn += dt

    # Check if enough time has passed
    def shouldSpawn(self) -> bool:
        return self.dtSpawn >= self.dftSpawnRate

    # Build pipe
    def spawn(self, passed_count: int = 0) -> Pipe:
        # Choose orientation based on patterns
        orientation = self.currPattern[self.patternIdx]
        self.patternIdx += 1

        # Choose new pattern if this one was completed
        if self.patternIdx >= len(self.currPattern):
            self.currPattern = random.choice(self.spawnPatterns)
            self.patternIdx = 0

        # Always spawn from the right
        newX = self.screen.get_width() + 20
        pipe_height = self._computePipeHeight(passed_count)

        # Place pipe based on orientation
        match (orientation):
            case "top":
                newY = random.randint(-self.edge, 0)
            case "bottom":
                newY = random.randint(
                    self.screen.get_height() - pipe_height,
                    self.screen.get_height() - self.edge,
                )

        # Reset time between respawns
        self.dtSpawn = 0.0

        # Return the new pipe
        return Pipe(
            screen=self.screen,
            currPos=pygame.Vector2(newX, newY),
            velocity=self.dftVelocity,
            orientation=orientation,
            sprite=chooseSprite(self.sprites),
            height=pipe_height
        )
