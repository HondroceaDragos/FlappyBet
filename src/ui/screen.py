import pygame
from enum import Enum

# 'ScreenComputer' class declaration and definition
class ScreenComputer:
    # All aspect ratios - should be 16:9 on all displays
    class AspectRatios(Enum):
        HEIGHT_PTG = 3 / 4
        WIDTH_BY_HEIGHT = 16 / 9

    # Virtual screen parameters
    _vScreenWidth = 1280
    _vScreenHeight = 720

    # Virtual screen surface
    _vScreen = pygame.Surface((_vScreenWidth, _vScreenHeight))

    # Compute both real and virtual screens
    @staticmethod
    def getScreen():
        displayHeight = pygame.display.Info().current_h
        screenHeight = int(ScreenComputer.AspectRatios.HEIGHT_PTG.value * displayHeight)
        screenWidth = int(ScreenComputer.AspectRatios.WIDTH_BY_HEIGHT.value * screenHeight)

        screen = pygame.display.set_mode((screenWidth, screenHeight))

        return screen, ScreenComputer._vScreen
    
    # Resize the virtual screen - avoid stretching
    @staticmethod
    def rescaleVirtualScreen(screen: pygame.Surface):
        scale = min(screen.get_width() / ScreenComputer._vScreenWidth,
                    screen.get_height() / ScreenComputer._vScreenHeight)

        return pygame.transform.smoothscale(ScreenComputer._vScreen,
            (int(scale * ScreenComputer._vScreenWidth),
             int(scale * ScreenComputer._vScreenHeight)))
    
    # Center the virtual screen - coords.
    @staticmethod
    def getOffset(screen: pygame.Surface):
        return ((screen.get_width() - ScreenComputer._vScreenWidth) // 2), \
                ((screen.get_height() - ScreenComputer._vScreenHeight) // 2)
    
    
