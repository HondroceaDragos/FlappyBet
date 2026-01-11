import pygame
import random
from ._abs_state import absState


class SlotsState(absState):
    # Probabilities
    P_DIAMOND = 0.25
    P_IRON = 0.55
    P_BOMB = 0.20

    def onEnter(self) -> None:
        # Ensure you have a bank to work with (score from game over)
        if not hasattr(self.master, "bank"):
            self.master.bank = getattr(self.master, "lastScore", 0)

        # Default bet: clamp to [0..bank]
        self.master.bet = 0

        # Load sprites (scale later in draw when we know window size)
        self._sprites_raw = {
            "iron": pygame.image.load("../assets/sprites/slotsSprites/iron2.png").convert_alpha(),
            "diamond": pygame.image.load("../assets/sprites/slotsSprites/diamond.png").convert_alpha(),
            "bomb": pygame.image.load("../assets/sprites/slotsSprites/bomb.png").convert_alpha(),
        }

        # Current reel result (start with something)
        self.result = ["iron", "iron", "iron"]
        self.last_message = "Press SPIN"
        self.last_delta = 0  # how much bank changed last spin

        # Basic “spin animation” state
        self.spinning = False
        self.spin_time = 0.0
        self.spin_duration = 0.8  # seconds

    def onExit(self) -> None:
        pass

    def _weighted_symbol(self) -> str:
        r = random.random()
        if r < self.P_DIAMOND:
            return "diamond"
        if r < self.P_DIAMOND + self.P_IRON:
            return "iron"
        return "bomb"

    def _multiplier_no_bombs(self, a: int, b: int) -> float:
        # a = diamonds count, b = iron count, bombs=0 guaranteed
        if a == 3:
            return 5.0
        if b == 3:
            return 3.0
        if a == 2 and b == 1:
            return 4.0
        if b == 2 and a == 1:
            return 2.0
        return 0.0

    def _apply_payout(self) -> None:
        bank = self.master.bank
        bet = self.master.bet

        # Safety
        bet = max(0, min(bet, bank))
        self.master.bet = bet

        if bet == 0:
            self.last_message = "Bet is 0. Increase bet to spin."
            self.last_delta = 0
            return

        d = self.result.count("diamond")
        i = self.result.count("iron")
        b = self.result.count("bomb")

        # Bomb rules
        if b >= 2:
            # Lose everything
            self.master.bank = 0
            self.last_delta = -bank
            self.last_message = f"{b} BOMBS! You lost EVERYTHING."
            self.master.bet = 0
            return

        if b == 1:
            # Lose bet only
            self.master.bank = bank - bet
            self.last_delta = -bet
            self.last_message = "BOMB! You lost your bet."
            self.master.bet = 0
            return

        # No bombs => multiplier payouts
        mult = self._multiplier_no_bombs(d, i)

        if mult <= 0.0:
            # Not specified by your rules; best default: lose bet
            self.master.bank = bank - bet
            self.last_delta = -bet
            self.last_message = "No combo. You lost your bet."
            return

        # Interpret "2x / 3x" as total return multiplier
        # new_bank = bank - bet + bet*mult
        new_bank = bank - bet + int(round(bet * mult))
        self.last_delta = new_bank - bank
        self.master.bank = new_bank
        self.last_message = f"WIN! x{mult}"
        self.master.bet = 0

    def handler(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.master.switchGameState("gameOver")
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if self._back_rect.collidepoint(mx, my):
                    self.master.switchGameState("gameOver")
                    return

                if self._spin_rect.collidepoint(mx, my):
                    if self.master.bank <= 0:
                        self.last_message = "Bank is 0. No more spins."
                        self.last_delta = 0
                        return

                    if self.master.bet <= 0:
                        self.last_message = "Bet is 0. Increase bet to spin."
                        self.last_delta = 0
                        return
                    if not self.spinning:
                        self.spinning = True
                        self.spin_time = 0.0
                    return

                if self._bet_minus_rect.collidepoint(mx, my):
                    self.master.bet = max(0, self.master.bet - 1)
                    return

                if self._bet_plus_rect.collidepoint(mx, my):
                    self.master.bet = min(self.master.bank, self.master.bet + 1)
                    return

    def update(self) -> None:
        # Use engine dt if you want; simplest is a local clock tick
        # But your project already has engine dt; here we’ll use pygame time.
        dt = pygame.time.Clock().tick(60) / 1000.0

        if self.spinning:
            self.spin_time += dt

            # During spinning, show rapidly changing symbols
            self.result = [self._weighted_symbol() for _ in range(3)]

            if self.spin_time >= self.spin_duration:
                self.spinning = False
                # Finalize result once more (so it’s not dependent on last frame)
                self.result = [self._weighted_symbol() for _ in range(3)]
                self._apply_payout()

    def draw(self) -> None:
        screen = self.master.screen
        screen.fill((18, 18, 22))
        w, h = screen.get_size()

        title_font = pygame.font.Font(None, 110)
        ui_font = pygame.font.Font(None, 46)
        small_font = pygame.font.Font(None, 34)

        # Title
        title = title_font.render("SLOTS", True, (245, 245, 245))
        screen.blit(title, ((w - title.get_width()) // 2, 50))

        # Bank + Bet
        bank_text = ui_font.render(f"Bank: {self.master.bank}", True, (220, 220, 220))
        bet_text = ui_font.render(f"Bet: {self.master.bet}", True, (220, 220, 220))
        screen.blit(bank_text, (60, 160))
        screen.blit(bet_text, (60, 210))

        # Bet buttons
        btn_w, btn_h = 60, 46
        self._bet_minus_rect = pygame.Rect(250, 210, btn_w, btn_h)
        self._bet_plus_rect = pygame.Rect(320, 210, btn_w, btn_h)

        pygame.draw.rect(screen, (70, 70, 80), self._bet_minus_rect, border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), self._bet_minus_rect, 2, border_radius=10)
        pygame.draw.rect(screen, (70, 70, 80), self._bet_plus_rect, border_radius=10)
        pygame.draw.rect(screen, (220, 220, 220), self._bet_plus_rect, 2, border_radius=10)

        minus = ui_font.render("-", True, (240, 240, 240))
        plus = ui_font.render("+", True, (240, 240, 240))
        screen.blit(minus, (self._bet_minus_rect.x + 24, self._bet_minus_rect.y + 6))
        screen.blit(plus, (self._bet_plus_rect.x + 22, self._bet_plus_rect.y + 3))

        # ---- Slot Machine Frame ----
        frame_w = int(w * 0.75)
        frame_h = int(h * 0.35)
        frame_x = (w - frame_w) // 2
        frame_y = int(h * 0.36)

        frame_rect = pygame.Rect(frame_x, frame_y, frame_w, frame_h)

        # Outer frame: red border + yellow inner
        pygame.draw.rect(screen, (160, 30, 30), frame_rect, border_radius=20)
        inner = frame_rect.inflate(-18, -18)
        pygame.draw.rect(screen, (230, 190, 60), inner, border_radius=16)

        # 3 white windows inside
        pad = 26
        gap = 22
        window_w = (inner.w - 2 * pad - 2 * gap) // 3
        window_h = inner.h - 2 * pad

        win_y = inner.y + pad
        win_x0 = inner.x + pad

        windows = []
        for k in range(3):
            wx = win_x0 + k * (window_w + gap)
            rect = pygame.Rect(wx, win_y, window_w, window_h)
            windows.append(rect)
            pygame.draw.rect(screen, (245, 245, 245), rect, border_radius=12)
            pygame.draw.rect(screen, (40, 40, 40), rect, 3, border_radius=12)

        # Scale sprites to fit windows
        # Keep aspect ratio and padding
        scaled = {}
        for name, img in self._sprites_raw.items():
            target = int(min(window_w, window_h) * 0.75)
            scaled[name] = pygame.transform.smoothscale(img, (target, target))

        # Blit results
        for k, sym in enumerate(self.result):
            img = scaled[sym]
            rect = img.get_rect(center=windows[k].center)
            screen.blit(img, rect)

        # Spin button
        spin_w, spin_h = 240, 70
        self._spin_rect = pygame.Rect((w - spin_w) // 2, frame_rect.bottom + 30, spin_w, spin_h)

        spin_col = (60, 140, 255) if not self.spinning else (120, 120, 140)
        pygame.draw.rect(screen, spin_col, self._spin_rect, border_radius=16)
        pygame.draw.rect(screen, (30, 30, 30), self._spin_rect, 3, border_radius=16)

        spin_label = ui_font.render("SPIN", True, (255, 255, 255))
        screen.blit(
            spin_label,
            (self._spin_rect.x + (spin_w - spin_label.get_width()) // 2,
             self._spin_rect.y + (spin_h - spin_label.get_height()) // 2),
        )

        # Message
        msg = small_font.render(self.last_message, True, (220, 220, 220))
        screen.blit(msg, ((w - msg.get_width()) // 2, self._spin_rect.bottom + 18))

        # Back button
        back_w, back_h = 200, 60
        self._back_rect = pygame.Rect(40, h - back_h - 40, back_w, back_h)
        pygame.draw.rect(screen, (70, 70, 80), self._back_rect, border_radius=14)
        pygame.draw.rect(screen, (220, 220, 220), self._back_rect, 2, border_radius=14)
        back_label = ui_font.render("Back", True, (240, 240, 240))
        screen.blit(
            back_label,
            (self._back_rect.x + (back_w - back_label.get_width()) // 2,
             self._back_rect.y + (back_h - back_label.get_height()) // 2),
        )

        hint = small_font.render("ESC = Game Over", True, (150, 150, 150))
        screen.blit(hint, (40, h - 32))
