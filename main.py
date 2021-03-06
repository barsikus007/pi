#!/usr/bin/python3.7
import os
import sys
import math
import time

import pygame
from gpiozero import Motor, Robot

from laboratory import scan


def joy_to_motor_bad(joy_x, joy_y):
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


def joy_to_motor(joy_x, joy_y):
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


def joy_to_motor_best(joy_x, joy_y):
    """Joystick single stick map converter"""
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
    return -left, -right


def calculate_diff(left, right, nom_left, nom_right, diff=0.01):
    """Soft acceleration mode calculator"""
    if abs(left - nom_left) > diff:
        direction = left - nom_left > 0
        nom_left += diff*(direction-1) + diff*direction
        left = nom_left
    if abs(right - nom_right) > diff:
        direction = right - nom_right > 0
        nom_right += diff*(direction-1) + diff*direction
        right = nom_right
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
    robot = Robot((27, 4), (6, 5))
    fork = Motor(15, 23)
    lift = Motor(20, 21)
    print('Pins OK')
    try:
        axes = {}
        d_pad = '(0, 0) '
        buttons = []
        acceleration_mode = False
        stick_mode = False
        forward = False
        d_pad_x, d_pad_y = 0, 0
        nom_left, nom_right = 0, 0
        while True:
            try:
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.JOYBUTTONDOWN:
                        buttons.append(str(event.button))
                        if event.button == 1:
                            # switch soft acceleration mode
                            acceleration_mode = not acceleration_mode
                        elif event.button == 2:
                            try:
                                # blocking scan function
                                scan()
                                try:
                                    buttons.remove(str(event.button))
                                except ValueError:
                                    pass
                            except Exception as e:
                                print(f'\r{e}')
                        elif event.button == 3:
                            # switch control map
                            stick_mode = not stick_mode
                    elif event.type == pygame.JOYBUTTONUP:
                        try:
                            buttons.remove(str(event.button))
                        except ValueError:
                            pass
                    elif event.type == pygame.JOYAXISMOTION:
                        if abs(event.value) > 0.1:
                            axes[event.axis] = f'{event.value:+.4f}'
                        else:
                            axes[event.axis] = f'{0.0:+.4f}'
                    elif event.type == pygame.MOUSEMOTION:
                        pass  # print(event.rel, event.buttons)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pass
                    elif event.type == pygame.MOUSEBUTTONUP:
                        pass
                    elif event.type == pygame.JOYHATMOTION:
                        d_pad = f'{event.value} '
                        d_pad_x, d_pad_y = event.value
                    else:
                        print(event)

                    # logging and writing to motors
                    buttons.sort(key=lambda x: int(x))
                    ax = list(axes.items())
                    ax.sort(key=lambda x: x[0])
                    left, right = -float(axes.get(1, '+0.0')), -float(axes.get(4, '+0.0'))
                    if stick_mode:
                        left, right = joy_to_motor_best(-float(axes.get(0, '+0.0')), -float(axes.get(1, '+0.0')))
                    if acceleration_mode:
                        left, right, nom_left, nom_right = calculate_diff(left, right, nom_left, nom_right, diff=0.005)
                    if forward:
                        left, right = 0.1, 0.1
                    print(
                        '\rButtons: ' + d_pad + ' '.join(buttons) + ' Axes: ' + '; '.join([f'{k}: {v}' for k, v in ax]),
                        end=f'     ({left}, {right})'
                    )
                    robot.value = (left, right)
                    lift.value = -d_pad_y
                    fork.value = -d_pad_x

            except Exception as e:
                print(f'\r{e}')

    except KeyboardInterrupt:
        print("\rEXITING NOW")
        j.quit()


def main():
    # MAC address of gamepad
    mac = '90:89:5F:07:35:43'
    try:
        os.putenv('DISPLAY', ':0.0')
        pygame.display.init()
        pygame.display.set_mode((1, 1))
        pygame.joystick.init()
        j = pygame.joystick.Joystick(0)
        j.init()
        print('Initialized!')
        joystick_loop(j)
    except pygame.error as e:
        # Kludge to connect to DualShock
        try:
            from traceback import format_exc
            print(e)
            print(type(e))
            print(format_exc())
            print('Connecting...')
            os.system(fr"/bin/echo -e 'connect {mac} \n' | bluetoothctl")
            # os.system(f'chmod +x {sys.argv[0]}')
            time.sleep(5)
            os.execv(sys.executable, ['python3'] + sys.argv)
        except Exception as e:
            print(e, type(e))
    except Exception as e:
        print(e, type(e))


if __name__ == '__main__':
    main()
    pygame.quit()
