import os
import sys
import time

import pygame
# from gpiozero import *

from laboratory import scan


latest = time.time()


def delta():
    global latest
    print(time.time() - latest)
    latest = time.time()
    return time.time()


def joystick_init():
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    return j


def joystick_loop(j,):
    # motor = Motor(12, 13)
    try:
        axes = {}
        dpad = '(0, 0) '
        buttons = []
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    buttons.append(str(event.button))
                    if event.button == 0:
                        scan()
                elif event.type == pygame.JOYBUTTONUP:
                    try:
                        buttons.remove(str(event.button))
                    except ValueError:
                        pass
                    if event.button == 0:
                        pass  # lab_check()
                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) > 0.1:
                        axes[event.axis] = f'{event.value:+.1f}'
                    else:
                        axes[event.axis] = f'{0.0:+.1f}'
                    if event.axis == 1:
                        pass
                        # motor.source = event.value
                elif event.type == pygame.MOUSEMOTION:
                    pass  # print(event.rel, event.buttons)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                elif event.type == pygame.JOYHATMOTION:
                    dpad = f'{event.value} '
                else:
                    print(event)
                buttons.sort(key=lambda x: int(x))
                ax = list(axes.items())
                ax.sort(key=lambda x: x[0])
                print('\rButtons: ' + dpad + ' '.join(buttons) + ' Axes: ' + '; '.join([f'{k}: {v}' for k, v in ax]), end='')

    except KeyboardInterrupt:
        print("\rEXITING NOW")
        j.quit()


def main():
    delta()
    j = joystick_init()
    joystick_loop(j)


if __name__ == '__main__':
    main()
    pygame.quit()
