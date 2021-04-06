import math
import time

import pygame

from gpiozero import *

# from laboratory import scan


latest = time.time()


def delta():
    global latest
    print(time.time() - latest)
    latest = time.time()
    return time.time()


def joy_to_motor_polar(joy_x, joy_y):
    # convert to polar coordinates
    theta = math.atan2(joy_y, joy_x)
    r = math.sqrt(joy_x * joy_x + joy_y * joy_y)
    # this is the maximum r for a given angle
    if abs(joy_x) > abs(joy_y):
        max_r = abs(r / joy_x)
    elif abs(joy_y) > abs(joy_x):
        max_r = abs(r / joy_y)
    else:
        return 0, 0
    # this is the actual throttle
    magnitude = r / max_r
    turn_damping = 3.0  # for example
    left = magnitude * (math.sin(theta) + math.cos(theta) / turn_damping)
    right = magnitude * (math.sin(theta) - math.cos(theta) / turn_damping)
    if left > 1:
        left = 1.0
    elif left < -1:
        left = -1.0
    if right > 1:
        right = 1.0
    elif right < -1:
        right = -1.0
    return -left, -right


def joy_to_motor_alt(joy_x, joy_y):
    left = joy_x * math.sqrt(2.0) / 2.0 + joy_y * math.sqrt(2.0) / 2.0
    right = -joy_x * math.sqrt(2.0) / 2.0 + joy_y * math.sqrt(2.0) / 2.0
    if left > 1:
        left = 1.0
    elif left < -1:
        left = -1.0
    if right > 1:
        right = 1.0
    elif right < -1:
        right = -1.0
    return left, right


def joy_to_motor(joy_x, joy_y):
    # Get X and Y from the Joystick, do whatever scaling and calibrating you need to do based on your hardware.
    # Invert X
    joy_y = -joy_y
    # Calculate R+L (Call it V):
    v = (100 - abs(joy_x)) * (joy_y / 100) + joy_y
    # Calculate R-L (Call it W):
    w = (100-abs(joy_y)) * (joy_x/100) + joy_x
    # Calculate R:
    right = (v-w) / 2
    left = (v+w) / 2
    if left > 1:
        left = 1.0
    elif left < -1:
        left = -1.0
    if right > 1:
        right = 1.0
    elif right < -1:
        right = -1.0
    return left, right


def joystick_init():
    pygame.init()
    j = pygame.joystick.Joystick(0)
    j.init()
    return j


def joystick_loop(j, ):
    robot = Robot((6, 5), (17, 27))
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
                        pass  # scan()
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
                # left, right = joy_to_motor_polar(float(axes.get(0, '+0.0')), float(axes.get(1, '+0.0')))
                print('\rButtons: ' + dpad + ' '.join(buttons) + ' Axes: ' + '; '.join([f'{k}: {v}' for k, v in ax]), end=f'')  # ({left}, {right})')
                robot.left(float(axes.get(1, '+0.0')))
                robot.right(float(axes.get(3, '+0.0')))

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
