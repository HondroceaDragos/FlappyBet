import pygame
from ._abs_state import absState


class HelpState(absState):
    def onEnter(self) -> None:
        # Which section is selected: None / "game" / "slots"
        self._selected = None

    def onExit(self) -> None:
        pass

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.master.switchGameState("mainMenu")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if hasattr(self, "_back_rect") and self._back_rect.collidepoint(mx, my):
                    self.master.switchGameState("mainMenu")
                    return

                if hasattr(self, "_game_rules_rect") and self._game_rules_rect.collidepoint(mx, my):
                    self._selected = "game"
                    return

                if hasattr(self, "_slot_rules_rect") and self._slot_rules_rect.collidepoint(mx, my):
                    self._selected = "slots"
                    return

    def update(self) -> None:
        pass

    def draw(self) -> None:
        screen = self.master.screen
        screen.fill((18, 18, 22))
        w, h = screen.get_size()

        title_font = pygame.font.Font(None, 110)
        header_font = pygame.font.Font(None, 56)
        text_font = pygame.font.Font(None, 42)
        hint_font = pygame.font.Font(None, 34)

        mx, my = pygame.mouse.get_pos()

        # Title
        title = title_font.render("Help", True, (240, 240, 240))
        screen.blit(title, ((w - title.get_width()) // 2, 60))

        # Buttons row (Game Rules / Slot Rules)
        btn_w, btn_h = 360, 72
        gap = 26
        total_w = btn_w * 2 + gap
        x0 = (w - total_w) // 2
        y_btn = 180

        self._game_rules_rect = pygame.Rect(x0, y_btn, btn_w, btn_h)
        self._slot_rules_rect = pygame.Rect(x0 + btn_w + gap, y_btn, btn_w, btn_h)

        def draw_button(rect: pygame.Rect, label: str, selected: bool = False):
            hovered = rect.collidepoint(mx, my)
            if hovered:
                fill = (60, 140, 255)  # hover blue
            else:
                fill = (90, 90, 110) if selected else (70, 70, 80)

            pygame.draw.rect(screen, fill, rect, border_radius=16)
            pygame.draw.rect(screen, (220, 220, 220), rect, 3, border_radius=16)

            t = header_font.render(label, True, (255, 255, 255))
            screen.blit(
                t,
                (rect.x + (rect.w - t.get_width()) // 2,
                 rect.y + (rect.h - t.get_height()) // 2),
            )

        draw_button(self._game_rules_rect, "Game Rules", selected=(self._selected == "game"))
        draw_button(self._slot_rules_rect, "Slot Rules", selected=(self._selected == "slots"))

        # Content panel
        panel_w = int(w * 0.78)
        panel_h = int(h * 0.42)
        panel_x = (w - panel_w) // 2
        panel_y = y_btn + btn_h + 30
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        pygame.draw.rect(screen, (245, 245, 245), panel, border_radius=18)
        pygame.draw.rect(screen, (30, 30, 30), panel, 3, border_radius=18)

        # Text content
        padding = 26
        cursor_y = panel_y + padding

        def blit_line(txt: str, bold: bool = False):
            nonlocal cursor_y
            font = header_font if bold else text_font
            color = (20, 20, 20)
            surf = font.render(txt, True, color)
            screen.blit(surf, (panel_x + padding, cursor_y))
            cursor_y += surf.get_height() + 10

        if self._selected is None:
            blit_line("Choose a section above.", bold=True)
            blit_line("Click Game Rules or Slot Rules to show info.")
        elif self._selected == "game":
            blit_line("RULES", bold=True)
            blit_line("• Avoid the stalactites and stalagmites")
            blit_line("• Don't touch the lava (and beware of fireballs)")
            blit_line("• You can't ride the minecarts")
        else:
            blit_line("SLOT RULES", bold=True)
            blit_line("• 3 DIAMONDS = 5x the bet")
            blit_line("• 3 IRON INGOTS = 3x the bet")
            blit_line("• 2 DIAMONDS + 1 IRON = 4x the bet")
            blit_line("• 2 IRON INGOTS + 1 DIAMOND = 2x the bet")
            blit_line("• 1 BOMB = LOSE THE BET")
            blit_line("• 2 OR 3 BOMBS = LOSE ALL YOUR POINTS")

        # Back button (hover blue)
        back_w, back_h = 260, 70
        back_x = (w - back_w) // 2
        back_y = h - back_h - 80
        self._back_rect = pygame.Rect(back_x, back_y, back_w, back_h)

        hovered_back = self._back_rect.collidepoint(mx, my)
        back_fill = (60, 140, 255) if hovered_back else (70, 70, 80)

        pygame.draw.rect(screen, back_fill, self._back_rect, border_radius=16)
        pygame.draw.rect(screen, (220, 220, 220), self._back_rect, 3, border_radius=16)

        label = header_font.render("Back", True, (255, 255, 255))
        screen.blit(
            label,
            (back_x + (back_w - label.get_width()) // 2,
             back_y + (back_h - label.get_height()) // 2),
        )

        hint = hint_font.render("Press ESC to return", True, (160, 160, 160))
        screen.blit(hint, ((w - hint.get_width()) // 2, h - 32))
