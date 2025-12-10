import pygame

from player import Player
from enemy import Enemy
from engine import PhysicsEngine
from master import GameMaster

# ======================= #
########## TO DO ##########
# ======================= #

# Add a background
# Add custom state support (right now we only have the game window)
# Think about settings in the future (not just 1280 by 720 - 60 fps)

# Add slots class

# Start the game window
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Initialize the master 
player = Player(screen = screen, radius = 40)
engine = PhysicsEngine(screen = screen, dt = 0, forceCoeff = 275)
enemy = Enemy(screen = screen)
gameMaster = GameMaster(screen, player, engine, enemy, True)

# Heart of the game
while gameMaster.running:
    screen.fill("white")
    gameMaster.update()
    pygame.display.flip()

pygame.quit()