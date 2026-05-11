from dataclasses import dataclass
from typing import Tuple


@dataclass
class CockpitMode:
    name: str
    display_name: str
    ambient_color: Tuple[int, int, int]
    ambient_color_name: str
    music_file: str
    ui_overlay: str
    ac_temperature: int
    ac_fan_speed: str
    ac_direction: str


DYNAMIC_MODE = CockpitMode(
    name="dynamic",
    display_name="Dynamic Mode",
    ambient_color=(255, 80, 0),
    ambient_color_name="Warm Orange",
    music_file="sounds/dynamic_rhythm.wav",
    ui_overlay="images/dynamic_overlay.png",
    ac_temperature=18,
    ac_fan_speed="High",
    ac_direction="Face (Cool)",
)

REST_MODE = CockpitMode(
    name="rest",
    display_name="Rest Mode",
    ambient_color=(80, 120, 255),
    ambient_color_name="Cool Blue",
    music_file="sounds/rest_soothing.wav",
    ui_overlay="images/rest_overlay.png",
    ac_temperature=26,
    ac_fan_speed="Low",
    ac_direction="Feet (Warm)",
)
