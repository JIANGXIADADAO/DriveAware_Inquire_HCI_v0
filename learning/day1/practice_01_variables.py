"""
Day 1 - Practice 1: Python fundamentals warm-up.

Just reviewing the basics before diving into computer vision.
Focus: clean functions, type hints, no magic numbers.
"""

# ------------------------------------------------------------------
# 1. Variables and basic types
# ------------------------------------------------------------------
name: str = "Alice"
age: int = 25
height_m: float = 1.68
is_student: bool = True

print(f"{name} is {age} years old, {height_m}m tall. Student: {is_student}")

# ------------------------------------------------------------------
# 2. Lists and loops
# ------------------------------------------------------------------
temperatures: list[float] = [21.5, 22.0, 23.1, 24.5, 25.0, 26.2, 27.0]

# Find the average temperature "manually" (yes, sum()/len() exists)
total = 0.0
count = 0
for temp in temperatures:
    total += temp
    count += 1
average = total / count
print(f"Average temperature over {count} readings: {average:.1f}C")

# ------------------------------------------------------------------
# 3. Functions with clear purpose
# ------------------------------------------------------------------
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit. One job only."""
    return celsius * 9.0 / 5.0 + 32.0


def is_warm(temp_c: float, threshold: float = 25.0) -> bool:
    """Check if a temperature is above the warm threshold."""
    return temp_c > threshold


for temp in temperatures:
    feeling = "warm" if is_warm(temp) else "cool"
    print(f"  {temp:.1f}C ({celsius_to_fahrenheit(temp):.1f}F) -- {feeling}")

# ------------------------------------------------------------------
# 4. Dictionaries for structured data
# ------------------------------------------------------------------
cabin_modes = {
    "dynamic": {"color": (255, 80, 0), "temp": 18, "fan": "High"},
    "rest":    {"color": (80, 120, 255), "temp": 26, "fan": "Low"},
}

for mode_name, settings in cabin_modes.items():
    print(f"\n{mode_name.upper()} MODE:")
    print(f"  Color:   RGB{settings['color']}")
    print(f"  Temp:    {settings['temp']}C")
    print(f"  Fan:     {settings['fan']}")
