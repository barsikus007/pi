#!/usr/bin/python3
import os
import sys
import math
import time

import pygame
from gpiozero import *

# from laboratory import scan


def joy_to_motor_polar(joy_x, joy_y):
    joy_y = -joy_y
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


def joy_to_motor_best(joy_x, joy_y):
    left = joy_x * math.sqrt(2.0) / 2.0 + joy_y * math.sqrt(2.0) / 2.0
    right = -joy_x * math.sqrt(2.0) / 2.0 + joy_y * math.sqrt(2.0) / 2.0
    # Invert III and IV zones of xy plot
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


def calculate_diff(left, right, nom_left, nom_right, diff=0.1):
    if abs(left - nom_left) > diff:
        direction = left - nom_left > 0
        left += diff*(direction-1) + diff*direction
    if abs(right - nom_right) > diff:
        direction = right - nom_right > 0
        right += diff*(direction-1) + diff*direction
    if left > 1:
        left = 1.0
    elif left < -1:
        left = -1.0
    if right > 1:
        right = 1.0
    elif right < -1:
        right = -1.0
    return left, right, left, right


def joystick_loop(j, ):
    robot = Robot((5, 6), (17, 27))
    try:
        axes = {}
        d_pad = '(0, 0) '
        buttons = []
        acceleration_mode = False
        nom_left, nom_right = 0, 0
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    buttons.append(str(event.button))
                    if event.button == 0:
                        pass  # scan()
                    elif event.button == 1:
                        acceleration_mode = not acceleration_mode
                    elif event.button == 2:
                        pass  # doors_open()
                elif event.type == pygame.JOYBUTTONUP:
                    try:
                        buttons.remove(str(event.button))
                    except ValueError:
                        pass
                elif event.type == pygame.JOYAXISMOTION:
                    if abs(event.value) > 0.1:
                        axes[event.axis] = f'{event.value:+.1f}'
                    else:
                        axes[event.axis] = f'{0.0:+.1f}'
                elif event.type == pygame.MOUSEMOTION:
                    pass  # print(event.rel, event.buttons)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                elif event.type == pygame.JOYHATMOTION:
                    d_pad = f'{event.value} '
                else:
                    pass  # print(event)
                buttons.sort(key=lambda x: int(x))
                ax = list(axes.items())
                ax.sort(key=lambda x: x[0])
                right, left = float(axes.get(1, '+0.0')), float(axes.get(4, '+0.0'))
                # left, right = joy_to_motor(float(axes.get(0, '+0.0')), float(axes.get(1, '+0.0')))
                if acceleration_mode:
                    left, right, nom_left, nom_right = calculate_diff(left, right, nom_left, nom_right, diff=0.1)
                print(
                    '\rButtons: ' + d_pad + ' '.join(buttons) + ' Axes: ' + '; '.join([f'{k}: {v}' for k, v in ax]),
                    end=f'     ({left}, {right})'
                )
                robot.value = (left, right)

    except KeyboardInterrupt:
        print("\rEXITING NOW")
        j.quit()


def main():
    mac = '90:89:5F:07:35:43'
    try:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.display.set_mode([0, 0])
        j = pygame.joystick.Joystick(0)
        j.init()
    except pygame.error as e:
        print(e)
        print('Connecting...')
        os.system(fr"/bin/echo -e 'connect {mac} \n' | bluetoothctl")
        # os.system(f'chmod +x {sys.argv[0]}')
        time.sleep(5)
        os.execv(sys.executable, ['python3'] + sys.argv)
    joystick_loop(j)


if __name__ == '__main__':
    main()
    pygame.quit()
