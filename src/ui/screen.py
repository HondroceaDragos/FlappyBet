import pygame
from enum import Enum


# 'ScreenComputer' class declaration and definition
class ScreenComputer:
    class Scales(Enum):
        HEIGHT_SCALE = 0.8

    # Virtual screen parameters
    _vScreenHeight = 720

    # Compute both real and virtual screens
    @staticmethod
    def getScreen():
        displayHeight = pygame.display.Info().current_h
        displayWidth = pygame.display.Info().current_w

        screenHeight = int(ScreenComputer.Scales.HEIGHT_SCALE.value * displayHeight)
        screenWidth = int(screenHeight * (displayWidth / displayHeight))

        screen = pygame.display.set_mode((screenWidth, screenHeight))

        _vScreenWidth = int(
            ScreenComputer._vScreenHeight * (screenWidth / screenHeight)
        )

        vScreen = pygame.Surface((_vScreenWidth, ScreenComputer._vScreenHeight))

        return screen, vScreen

    # Resize the virtual screen - avoid stretching
    @staticmethod
    def rescaleVirtualScreen(screen: pygame.Surface, vScreen: pygame.Surface):
        return pygame.transform.smoothscale(vScreen, screen.get_size())
