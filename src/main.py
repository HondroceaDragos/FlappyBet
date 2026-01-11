# =========================
# MODIFY FILE: src/main.py
# (minimal changes: remove PipeFactory creation; master no longer needs it)
# =========================
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
import sys

from entities import Player
from core import PhysicsEngine
from gameplay import GameMaster
from ui import ScreenComputer
from sound import SoundManager
from debugger import Debugger

if len(sys.argv) == 2:
    if sys.argv[1] == "-d":
        Debugger.enable()
    else:
        print("To start the debugger, please use '-d' ")
        sys.exit()

pygame.init()
pygame.mixer.init()

screen, vScreen = ScreenComputer.getScreen()
vScreen = ScreenComputer.rescaleVirtualScreen(screen, vScreen)

player = Player(screen=vScreen, radius=35)
engine = PhysicsEngine(screen=vScreen, dt=0)
sound = SoundManager()

# factory is now unused; pass None
gameMaster = GameMaster(vScreen, engine, player, None, sound, True)

if Debugger.STATE:
    gameMaster.switchGameState(Debugger.STATE)

while gameMaster.running:
    # NOTE: you may want to blit AFTER update for no 1-frame lag,
    # but leaving your structure unchanged is fine.
    screen.blit(vScreen, (0, 0))
    gameMaster.update()
    pygame.display.flip()

pygame.quit()
