import time
import asyncio

import cv2
import pygame
import numpy as np
from pymata_express import pymata_express


init_time = time.time()


def joystick_init():
    pygame.init()
    pygame.display.set_mode((1, 1))
    # ssh -X
    j = pygame.joystick.Joystick(0)
    j.init()
    return j


def joystick_loop_ard(j, board):
    try:
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.value == 0:
                        pass  # lab_check()
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 1:
                        value = int(event.value * 255)
                        if value != 0 and abs(value) < 20:
                            continue
                        print(value)
                        if value > 20:
                            board.pwm(3, abs(value))
                        elif value < -20:
                            board.pwm(2, abs(value))
                        else:
                            board.pwm(2, 0)
                            board.pwm(3, 0)

    except KeyboardInterrupt:
        print("EXITING NOW")
        j.quit()


def arduino_init(delay=2):
    return pymata_express.PymataExpress(arduino_wait=delay)


def delta(latest: float = None):
    if latest:
        print(time.time() - latest)
    else:
        print(time.time() - init_time)
    return time.time()


class Board:
    def __init__(self, board, loop, lat):
        self.board = board
        self.loop = loop
        self.lat = lat

    def init_pwm_pins(self, pins):
        self.loop.run_until_complete(self._init_pwm_pins(pins))

    async def _init_pwm_pins(self, pins):
        for pin in pins:
            await self.board.set_pin_mode_pwm(pin)

    async def pwm(self, pin, value):
        self.loop.run_until_complete(self._pwm(pin, value))

    async def _pwm(self, pin, value):
        value = value % 256
        board = self.board
        await board.set_pin_mode_pwm(pin)
        await board.pwm_write(pin, value)


def main():
    loop = asyncio.get_event_loop()
    lat = delta()
    brd = Board(arduino_init(1), loop, lat)
    brd.init_pwm_pins([2, 3, 13])
    brd.pwm(2, 255)
    j = joystick_init()
    joystick_loop_ard(j, brd)


if __name__ == '__main__':
    main()
    pygame.quit()
