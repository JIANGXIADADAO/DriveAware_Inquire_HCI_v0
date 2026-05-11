import os
import pygame


ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets"
)


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.current_track = None
        self.music_enabled = True
        self._paused = False

    def play(self, mode):
        path = os.path.join(ASSETS_DIR, mode.music_file)
        if not os.path.exists(path):
            return
        if self.current_track == path:
            return
        self.current_track = path
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)

    def stop(self):
        pygame.mixer.music.stop()
        self.current_track = None

    def pause(self):
        if not self._paused:
            pygame.mixer.music.pause()
            self._paused = True

    def unpause(self):
        if self._paused:
            pygame.mixer.music.unpause()
            self._paused = False
