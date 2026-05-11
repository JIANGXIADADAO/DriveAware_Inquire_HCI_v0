import pygame
import config


class ClimateDisplay:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 32)

    def render(self, mode):
        y = 250
        for label, value in [
            ("Temperature", f"{mode.ac_temperature} C"),
            ("Fan Speed", mode.ac_fan_speed),
            ("Air Direction", mode.ac_direction),
        ]:
            text = f"{label}: {value}"
            surf = self.font.render(text, True, (200, 220, 255))
            rect = surf.get_rect(
                center=(config.WINDOW_WIDTH // 2, y)
            )
            self.screen.blit(surf, rect)
            y += 40
