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
from debugger import Debugger

# ======================= #
########## TO DO ##########
# ======================= #

# Add a background
# Think about settings in the future (not just 1280 by 720 - 60 fps)

# Add slots class

# Migth want to store screen parameters to not call get_... all the time

# Debugger usage prompt
if len(sys.argv) == 2:
    if sys.argv[1] == "-d":
        Debugger.enable()
    else:
        print("To start the debugger, please use '-d' ")
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

if Debugger.STATE:
    gameMaster.switchGameState(Debugger.STATE)

# Heart of the game
while gameMaster.running:
    screen.blit(vScreen, (0, 0))

    # Handle events
    gameMaster.update()

    pygame.display.flip()

pygame.quit()
