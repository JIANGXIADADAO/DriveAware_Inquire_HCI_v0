import config


class AmbientLight:
    def __init__(self):
        self.current_color = list(config.BG_COLOR)

    def update(self, target_color):
        for i in range(3):
            diff = target_color[i] - self.current_color[i]
            step = max(-config.COLOR_TRANSITION_SPEED,
                       min(config.COLOR_TRANSITION_SPEED, diff))
            self.current_color[i] += step

    def get_color(self):
        return tuple(int(c) for c in self.current_color)

    def snap_to(self, color):
        self.current_color = list(color)
