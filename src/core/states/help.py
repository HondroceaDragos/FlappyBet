import pygame
from ._abs_state import absState


class HelpState(absState):
    def onEnter(self) -> None:
        pass

    def onExit(self) -> None:
        pass

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.master.switchGameState("mainMenu")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self._back_rect.collidepoint(mx, my):
                    self.master.switchGameState("mainMenu")
                    return

    def update(self) -> None:
        pass

    def draw(self) -> None:
        self.master.screen.fill((18, 18, 22))
        w, h = self.master.screen.get_size()

        title_font = pygame.font.Font(None, 110)
        text_font = pygame.font.Font(None, 44)

        title = title_font.render("Help", True, (240, 240, 240))
        self.master.screen.blit(title, ((w - title.get_width()) // 2, 80))

        # Placeholder text (empty for now)
        msg = text_font.render("(", True, (180, 180, 180))
        self.master.screen.blit(msg, ((w - msg.get_width()) // 2, 200))

        # Back button
        btn_w, btn_h = 260, 70
        btn_x = (w - btn_w) // 2
        btn_y = h - btn_h - 90
        self._back_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

        pygame.draw.rect(self.master.screen, (70, 70, 80), self._back_rect, border_radius=14)
        pygame.draw.rect(self.master.screen, (220, 220, 220), self._back_rect, 3, border_radius=14)

        label = text_font.render("Back", True, (240, 240, 240))
        self.master.screen.blit(
            label,
            (btn_x + (btn_w - label.get_width()) // 2,
             btn_y + (btn_h - label.get_height()) // 2),
        )

        hint_font = pygame.font.Font(None, 34)
        hint = hint_font.render("Press ESC to return", True, (160, 160, 160))
        self.master.screen.blit(hint, ((w - hint.get_width()) // 2, h - 40))
