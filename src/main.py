import os

# Hide support prompt in console
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"

import pygame

from entities import Player
from entities import Enemy
from core import PhysicsEngine
from gameplay import GameMaster
from ui import ScreenComputer

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

pygame.init()

# Start the game window
screen, vScreen = ScreenComputer.getScreen()
vScreen = ScreenComputer.rescaleVirtualScreen(screen)

# Initialize the master 
player = Player(screen = vScreen, radius = 40)
engine = PhysicsEngine(screen = vScreen, dt = 0, frameRate = 60)
enemy = Enemy(screen = vScreen)
gameMaster = GameMaster(vScreen, player, engine, enemy, True)

# Debugger state selection
match sys.argv[1]:
    case "-m":
        gameMaster.currState = "mainMenu"
    case "-g":
        gameMaster.currState = "gameInProgress"

# Heart of the game
while gameMaster.running:
    # Display 1280x720 on all displays
    screen.blit(vScreen, ScreenComputer.getOffset(screen))

    # Handle events
    gameMaster.update()

    pygame.display.flip()

pygame.quit()