import pygame
from config import SettingsManager

# 'SoundManager' class declaration and definition
class SoundManager:
    def __init__(self):
        # Get the sound user preferences
        userPref = SettingsManager.getUserPreferences()

        # Custom sfx volume - fallback to 1.0
        self.sfxVolume = userPref.get("sfx", 1.0)

        # Load all sfx sounds
        self.sfx = {
            "playerJump": pygame.mixer.Sound("../assets/audio/sfx/playerJump.wav"),
            "playerDeath": pygame.mixer.Sound("../assets/audio/sfx/playerDeath.wav")
        }

        # Change their volume
        self.changeSfxVolume(self.sfxVolume)

        # Custom music volume - fallback to 1.0
        self.musicVolume = userPref.get("music", 1.0)

        # Where to find songs
        self.music = {
            "gameLoop": "../assets/audio/songs/gameLoop.wav",
            "mainMenu": "../assets/audio/songs/mainMenu.wav"
        }

        # No song is initially loaded
        self.currSong = None

        self.changeMusicVolume(self.musicVolume)

    # Play the specified sfx
    def playSfx(self, sound: str) -> None:
        if sound in self.sfx:
            self.sfx[sound].play()

    # Change volume of all sfx
    def changeSfxVolume(self, value: float):
        # Clamp volume [0.0, 1.0]
        self.sfxVolume = max(0.0, min(1.0, self.sfxVolume + value))

        for sfx in self.sfx.values():
            sfx.set_volume(self.sfxVolume)

    # Play the specified song
    def playMusic(self, song: str) -> None:
        if self.currSong == song:
            return
        
        if song in self.music:
            self.currSong = song
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.music[song])
            pygame.mixer.music.play(-1, fade_ms=500)

    # Change volume of all songs
    def changeMusicVolume(self, value: float):
        # Clamp volume [0.0, 1.0]
        self.musicVolume = max(0.0, min(1.0, self.musicVolume + value))
        pygame.mixer.music.set_volume(self.musicVolume)