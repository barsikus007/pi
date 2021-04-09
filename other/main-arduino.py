import pygame

pymata_ex = False

if pymata_ex:
    import asyncio as time
    from pymata_express import pymata_express
else:
    import time
    from pymata4 import pymata4


def joystick_init():
    pygame.init()
    joy = pygame.joystick.Joystick(0)
    joy.init()
    return joy


def loop_ard(joy, board):
    try:
        motor_l = (2, 3)
        motor_r = (4, 5)
        ax_x, ax_y = 0, 0
        dpad_x, dpad_y = 0, 0
        axes = {}
        buttons = []
        dpad_str = '(0, 0) '
        axes_str = {}
        buttons_str = []
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    buttons.append(event.button)
                    buttons_str.append(str(event.button))
                elif event.type == pygame.JOYBUTTONUP:
                    try:
                        buttons.remove(event.button)
                        buttons_str.remove(str(event.button))
                    except ValueError:
                        pass
                elif event.type == pygame.JOYAXISMOTION:
                    if event.value > 1:
                        _value = 1
                    elif event.value < -1:
                        _value = -1
                    else:
                        _value = event.value
                    if abs(_value) > 0.1:
                        axes_str[event.axis] = f'{_value:+.1f}'
                        axes[event.axis] = _value
                    else:
                        axes_str[event.axis] = f'{0.0:+.1f}'
                        axes[event.axis] = 0.0
                elif event.type == pygame.MOUSEMOTION:
                    pass  # print(event.rel, event.buttons_str)
                elif event.type == pygame.JOYHATMOTION:
                    dpad_str = f'{event.value} '
                    dpad_x, dpad_y = event.value
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    pass
                # else:
                #     print(event)
            buttons_str.sort(key=lambda x: int(x))
            ax = list(axes_str.items())
            ax.sort(key=lambda x: x[0])
            print(
                '\rButtons: ' + dpad_str + ' '.join(buttons_str) + ' Axes: ' + '; '.join([f'{k}: {v}' for k, v in ax]),
                end=''
            )

            if 0 in buttons:
                board.servo(6, 1)
            if 2 in buttons:
                board.servo(6, 180)
            if 1 in buttons:
                board.servo(2, 1)
            if 3 in buttons:
                board.servo(2, 180)

            if 0 not in buttons:
                board.servo(6, 87)
            if 2 not in buttons:
                board.servo(6, 87)
            if 1 not in buttons:
                board.servo(2, 89)
            if 3 not in buttons:
                board.servo(2, 89)

            if dpad_x == 1:
                board.forward(8, 9)
            elif dpad_x == -1:
                board.backward(8, 9)
            elif dpad_x == 0:
                board.stop(8, 9)

            if dpad_y == 1:
                board.forward(10, 11)
            elif dpad_y == -1:
                board.backward(10, 11)
            elif dpad_y == 0:
                board.stop(10, 11)

            for axis, value in axes.items():
                if axis == 3:
                    ax_x = value
                if axis == 2:
                    ax_y = -value

            if abs(ax_x) < 0.5:
                if ax_y > 0.5:
                    print('Вперед')
                    board.forward(*motor_l)
                    board.forward(*motor_r)

                if ax_y < -0.5:
                    print('Назад')
                    board.backward(*motor_l)
                    board.backward(*motor_r)

                if abs(ax_y) < 0.5:
                    print('Стоять!')
                    board.stop(*motor_l)
                    board.stop(*motor_r)

            if ax_x > 0.5:
                if abs(ax_y) < 0.25:
                    print('Вправо')
                    board.forward(*motor_l)
                    board.backward(*motor_r)

            if ax_x < -0.5:
                if abs(ax_y) < 0.25:
                    print('Влево')
                    board.backward(*motor_l)
                    board.forward(*motor_r)

            '''if ax_x < -0.75:   #влево-вперед
                if ax_y < -0.75:
                    board.pwm(2, 0)
                    board.pwm(3, 255)
                    board.pwm(4, 150)
                    board.pwm(5, 0)
                    board.motor(*motor_r, 150, 0)
            
            if ax_x > 0.75:  #влево-назад
                if ax_y > 0.75:
                    board.pwm(2, 255)
                    board.pwm(3, 0)
                    board.pwm(4, 0)
                    board.pwm(5, 150)'''

    except KeyboardInterrupt:
        print("EXITING NOW")
        joy.quit()


def arduino_init(delay=2):
    if pymata_ex:
        return pymata_express.PymataExpress(arduino_wait=delay)
    else:
        return pymata4.Pymata4(arduino_wait=delay)


class Board:
    def __init__(self, board):
        self.board = board
        self.pins = {
            'servo': {},
            'pwm': {},
        }

    def init_servo_pins(self, pins, val=89):
        if pymata_ex:
            pass
        else:
            for pin in pins:
                self.board.set_pin_mode_servo(pin)
                self.board.servo_write(pin, val)
                self.pins['servo'][pin] = val

    def init_pwm_pins(self, pins):
        if pymata_ex:
            pass
        else:
            for pin in pins:
                self.board.set_pin_mode_pwm_output(pin)
                self.pins['pwm'][pin] = 0

    def servo(self, pin, value):
        if self.pins['servo'][pin] != value:
            self.board.servo_write(pin, value)
            self.pins['servo'][pin] = value

    def pwm(self, pin, value):
        if self.pins['pwm'][pin] != value:
            self.board.pwm_write(pin, value)
            self.pins['pwm'][pin] = value

    def motor(self, pin_1, pin_2, value_1, value_2):
        if self.pins['pwm'][pin_1] != value_1:
            self.board.pwm_write(pin_1, value_1)
            self.pins['pwm'][pin_1] = value_1
        if self.pins['pwm'][pin_2] != value_2:
            self.board.pwm_write(pin_2, value_2)
            self.pins['pwm'][pin_2] = value_2

    def forward(self, pin_1, pin_2):
        self.motor(pin_1, pin_2, 255, 0)

    def stop(self, pin_1, pin_2):
        self.motor(pin_1, pin_2, 0, 0)

    def backward(self, pin_1, pin_2):
        self.motor(pin_1, pin_2, 0, 255)


def main():
    board = Board(arduino_init(4))
    board.init_pwm_pins([2, 3, 4, 5, 8, 9, 10, 11, 12])
    board.init_servo_pins([4], 89)  # сжатие расжатие локоть
    board.init_servo_pins([6], 89)
    joy = joystick_init()
    loop_ard(joy, board)


if __name__ == '__main__':
    main()
    pygame.quit()
