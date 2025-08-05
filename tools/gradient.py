#!/usr/bin/env python

# -----------------------------------------------------------------------------
#
# Colour gradient generator
#
# Author: Andrew Watson
# 
# -----------------------------------------------------------------------------

def hex_to_RGB(hex_colour: str) -> tuple[int, int, int]:
    if hex_colour.startswith("#"):
        hex_colour = hex_colour[1:]

    if len(hex_colour) != 6:
        raise ValueError("Invalid hex colour format. Expected 6 characters (e.g., 'RRGGBB').")

    r_hex = hex_colour[0:2]
    g_hex = hex_colour[2:4]
    b_hex = hex_colour[4:6]

    r = int(r_hex, 16)
    g = int(g_hex, 16)
    b = int(b_hex, 16)

    return (r, g, b)

# -----------------------------------------------------------------------------
def RGB_to_hex(rgb_colour: tuple[int, int, int]) -> str:
    r = str(hex(rgb_colour[0]))[2:]
    g = str(hex(rgb_colour[1]))[2:]
    b = str(hex(rgb_colour[2]))[2:]
    return f'#{r}{g}{b}'

# -----------------------------------------------------------------------------
def get_colour_gradient(colour1: str, colour2: str, num_steps: int):
    """
    Generates a linear colour gradient between two hexadecimal colours.

    Args:
        colour1: The starting colour in web hex format (#RRGGBB).
        colour2: The ending colour in web hex format (#RRGGBB).
        num_steps (int): The number of steps in the gradient.

    Returns:
        list: A list of web hex colours representing the required gradient.
    """
    gradient_colours = []
    colour1_rgb = hex_to_RGB(colour1)
    colour2_rgb = hex_to_RGB(colour2)

    for i in range(num_steps):
        # Calculate interpolation factor (0 to 1)
        t = i / (num_steps - 1) if num_steps > 1 else 0

        # Interpolate each colour component
        r = int(colour1_rgb[0] + (colour2_rgb[0] - colour1_rgb[0]) * t)
        g = int(colour1_rgb[1] + (colour2_rgb[1] - colour1_rgb[1]) * t)
        b = int(colour1_rgb[2] + (colour2_rgb[2] - colour1_rgb[2]) * t)

        gradient_colours.append(RGB_to_hex((r, g, b)))
    return gradient_colours

# Example usage:
start_colour = '#57bb8a'  # Green #57bb8a
mid_colour = '#ffffff'
end_colour = '#e67c73'    # Red #e67c73

steps = 10

gradient = get_colour_gradient(start_colour, mid_colour, steps)

for c in gradient:
    print(c)

gradient = get_colour_gradient(mid_colour, end_colour, steps)
for c in gradient[1:]:
    print(c)