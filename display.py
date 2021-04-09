# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This demo will fill the screen with white, draw a black box on top
and then print Hello World! in the center of the display

This example is for use on (Linux) computers that are using CPython with
Adafruit Blinka to support CircuitPython libraries. CircuitPython does
not support PIL/pillow (python imaging library)!
"""

import sys
import time

import board
import busio
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_pcd8544

# Parameters to Change
BORDER = 5
FONTSIZE = 10

spi = busio.SPI(board.SCK, MOSI=board.MOSI)
# dc = digitalio.DigitalInOut(board.D6)  # data/command
dc = digitalio.DigitalInOut(board.D12)  # data/command
cs = digitalio.DigitalInOut(board.CE0)  # Chip select
# reset = digitalio.DigitalInOut(board.D5)  # reset
reset = digitalio.DigitalInOut(board.D24)  # reset

display = adafruit_pcd8544.PCD8544(spi, dc, cs, reset)

# Contrast and Brightness Settings
display.bias = 4
display.contrast = 60

# Turn on the Backlight LED
# backlight = digitalio.DigitalInOut(board.D13)  # backlight
# backlight.switch_to_output()
# backlight.value = True

# Clear display.
display.fill(0)
display.show()
time.sleep(1)


# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
def make_image(text):
    text = str(text)
    image = Image.new("1", (display.width, display.height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a black background
    draw.rectangle((0, 0, display.width-1, display.height-1), outline=255, fill=0)

    # Draw a smaller inner rectangle
    draw.rectangle(
        (BORDER, BORDER, display.width - BORDER - 1, display.height - BORDER - 1),
        outline=0,
        fill=0,
    )

    # Load a TTF font.
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

    # Draw Some Text
    (font_width, font_height) = font.getsize(text)
    draw.text(
        (display.width // 2 - font_width // 2, display.height // 2 - font_height // 2),
        text,
        font=font,
        fill=255,
    )
    return image


def show(text):
    # Display image
    display.fill(0)
    display.show()
    time.sleep(1)
    image = make_image(text)
    display.image(image)
    display.show()
    # make blocking


if __name__ == '__main__':
    show('5 4 3 2 1')
