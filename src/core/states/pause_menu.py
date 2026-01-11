import pygame
from ._abs_state import absState
from config import SettingsManager


class PauseMenuState(absState):
    def onEnter(self) -> None:
        self.master.isPaused = True
        # Prevent dt “jump” when resuming
        self.master.engine.resetClock()

    def onExit(self) -> None:
        self.master.isPaused = False
        self.master.sound.playMusic("gameLoop")
        # Prevent dt including time spent paused
        self.master.engine.resetClock()

    def _clamp01(self, x: float) -> float:
        return max(0.0, min(1.0, x))

    def _set_music_volume(self, v: float) -> None:
        v = self._clamp01(v)
        # Set absolute volume (not incremental)
        self.master.sound.musicVolume = v
        pygame.mixer.music.set_volume(v)
        SettingsManager.setUserPreferences({"music": v})

    def _set_sfx_volume(self, v: float) -> None:
        v = self._clamp01(v)
        self.master.sound.sfxVolume = v
        for sfx in self.master.sound.sfx.values():
            sfx.set_volume(v)
        SettingsManager.setUserPreferences({"sfx": v})

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Resume run
                self.master.switchGameState("gameInProgress")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Handle clicks on volume bars
                # Music bar
                if self._music_bar_rect.collidepoint(mx, my):
                    t = (mx - self._music_bar_rect.x) / self._music_bar_rect.w
                    self._set_music_volume(t)

                # SFX bar
                if self._sfx_bar_rect.collidepoint(mx, my):
                    t = (mx - self._sfx_bar_rect.x) / self._sfx_bar_rect.w
                    self._set_sfx_volume(t)
                    # optional feedback sound
                    self.master.sound.playSfx("playerJump")

                # Exit button
                if self._exit_rect.collidepoint(mx, my):
                    self.master.switchGameState("mainMenu")
                    return

            if event.type == pygame.MOUSEMOTION and event.buttons[0]:
                mx, my = event.pos
                if self._music_bar_rect.collidepoint(mx, my):
                    t = (mx - self._music_bar_rect.x) / self._music_bar_rect.w
                    self._set_music_volume(t)
                if self._sfx_bar_rect.collidepoint(mx, my):
                    t = (mx - self._sfx_bar_rect.x) / self._sfx_bar_rect.w
                    self._set_sfx_volume(t)

    def update(self) -> None:
        # Freeze gameplay by doing NOTHING related to physics/spawn.
        # We still draw a paused overlay.
        pass

    def draw(self) -> None:
        # Draw the last gameplay frame as background
        # (We can re-render the scene using current objects without updating them.)
        self.master.screen.fill("white")
        self.master.player.draw()
        for pipe in self.master.pipes:
            pipe.draw()

        # Dim overlay
        overlay = pygame.Surface(self.master.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.master.screen.blit(overlay, (0, 0))

        w, h = self.master.screen.get_size()

        # Layout (compute rects every draw; simple and robust)
        panel_w = int(w * 0.65)
        panel_h = int(h * 0.55)
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(self.master.screen, (245, 245, 245), panel_rect, border_radius=16)
        pygame.draw.rect(self.master.screen, (30, 30, 30), panel_rect, 3, border_radius=16)

        # Title
        title_font = pygame.font.Font(None, 90)
        text_font = pygame.font.Font(None, 48)

        title = title_font.render("Paused", True, (20, 20, 20))
        self.master.screen.blit(title, (panel_x + 24, panel_y + 20))

        # Volume bars
        bar_x = panel_x + 40
        bar_w = panel_w - 80
        bar_h = 22

        music_label_y = panel_y + 120
        music_bar_y = music_label_y + 42

        sfx_label_y = music_bar_y + 50
        sfx_bar_y = sfx_label_y + 42

        # Store rects for click handling
        self._music_bar_rect = pygame.Rect(bar_x, music_bar_y, bar_w, bar_h)
        self._sfx_bar_rect = pygame.Rect(bar_x, sfx_bar_y, bar_w, bar_h)

        # Labels
        music_lbl = text_font.render("Music", True, (20, 20, 20))
        sfx_lbl = text_font.render("SFX", True, (20, 20, 20))
        self.master.screen.blit(music_lbl, (bar_x, music_label_y))
        self.master.screen.blit(sfx_lbl, (bar_x, sfx_label_y))

        # Draw bar backgrounds
        pygame.draw.rect(self.master.screen, (210, 210, 210), self._music_bar_rect, border_radius=10)
        pygame.draw.rect(self.master.screen, (210, 210, 210), self._sfx_bar_rect, border_radius=10)

        # Draw filled parts
        music_fill_w = int(bar_w * self.master.sound.musicVolume)
        sfx_fill_w = int(bar_w * self.master.sound.sfxVolume)

        if music_fill_w > 0:
            pygame.draw.rect(
                self.master.screen, (60, 140, 255),
                pygame.Rect(bar_x, music_bar_y, music_fill_w, bar_h),
                border_radius=10
            )
        if sfx_fill_w > 0:
            pygame.draw.rect(
                self.master.screen, (60, 140, 255),
                pygame.Rect(bar_x, sfx_bar_y, sfx_fill_w, bar_h),
                border_radius=10
            )

        # Exit button
        btn_w = 320
        btn_h = 64
        btn_x = panel_x + (panel_w - btn_w) // 2
        btn_y = panel_y + panel_h - btn_h - 20
        self._exit_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.master.screen, (220, 70, 70), self._exit_rect, border_radius=14)
        pygame.draw.rect(self.master.screen, (30, 30, 30), self._exit_rect, 3, border_radius=14)

        btn_text = text_font.render("Exit to Main Menu", True, (255, 255, 255))
        tx = btn_x + (btn_w - btn_text.get_width()) // 2
        ty = btn_y + (btn_h - btn_text.get_height()) // 2
        self.master.screen.blit(btn_text, (tx, ty))

        # Hint
        hint_font = pygame.font.Font(None, 36)
        hint = hint_font.render("Press ESC to resume", True, (60, 60, 60))
        self.master.screen.blit(hint, (panel_x + 24, panel_y + panel_h - 36))
