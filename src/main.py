import os

# Hide support prompt in console
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

from entities import Player
from entities import PipeFactory

from core import PhysicsEngine

from gameplay import GameMaster

from ui import ScreenComputer

from sound import SoundManager

import sys

# ======================= #
########## TO DO ##########
# ======================= #

# Add a background
# Think about settings in the future (not just 1280 by 720 - 60 fps)

# Add slots class

# Migth want to store screen parameters to not call get_... all the time

# Debugger usage prompt
if len(sys.argv) < 2:
    print("Usage:\n")
    print("-m: Start from main menu")
    print("-g: Start from gameplay section\n")
    sys.exit()

pygame.init()
pygame.mixer.init()

# Start the game window
screen, vScreen = ScreenComputer.getScreen()
vScreen = ScreenComputer.rescaleVirtualScreen(screen, vScreen)

# Initialize the master
player = Player(screen=vScreen, radius=35)
engine = PhysicsEngine(screen=vScreen, dt=0)
sound = SoundManager()
factory = PipeFactory(screen=vScreen)
gameMaster = GameMaster(vScreen, engine, player, factory, sound, True)

# Debugger state selection
match sys.argv[1]:
    case "-m":
        gameMaster.switchGameState("mainMenu")
    case "-g":
        gameMaster.switchGameState("gameInProgress")

# Heart of the game
while gameMaster.running:
    screen.blit(vScreen, (0, 0))

    # Handle events
    gameMaster.update()

    pygame.display.flip()

pygame.quit()
