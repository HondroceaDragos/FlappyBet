import os

# Hide support prompt in console
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame

from player import Player
from enemy import Enemy
from engine import PhysicsEngine
from master import GameMaster

import sys

# ======================= #
########## TO DO ##########
# ======================= #

# Add a background
# Add custom state support (right now we only have the game window) - DONE :D
# Think about settings in the future (not just 1280 by 720 - 60 fps)

# Add slots class

# Debugger usage prompt
if len(sys.argv) < 2:
    print("Usage:\n")
    print("-m: Start from main menu")
    print("-g: Start from gameplay section\n")
    sys.exit()

# Start the game window
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Initialize the master 
player = Player(screen = screen, radius = 40)
engine = PhysicsEngine(screen = screen, dt = 0, forceCoeff = 275)
enemy = Enemy(screen = screen)
gameMaster = GameMaster(screen, player, engine, enemy, True)

# Debugger state selection
match sys.argv[1]:
    case "-m":
        gameMaster.currState = "mainMenu"
    case "-g":
        gameMaster.currState = "gameInProgress"

# Heart of the game
while gameMaster.running:
    gameMaster.update()
    pygame.display.flip()

pygame.quit()