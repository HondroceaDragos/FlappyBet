import pygame
from abc import ABC, abstractmethod


# 'absState' abstract class declaration and definition
class absState(ABC):
    # All states interact with the master
    # but not with eachother
    def __init__(self, master):
        self.master = master

    # Each state has its own unique events
    @abstractmethod
    def handler(self, events: list[pygame.event.Event]) -> None:
        pass

    # Each state update the game in different ways
    @abstractmethod
    def update(self) -> None:
        pass

    # Each state draws different sprites
    @abstractmethod
    def draw(self) -> None:
        print("If this is shown in terminal, something bad happened!")
