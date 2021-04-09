# https://github.com/PedalPi/Raspberry-Physical/blob/master/component/pcd8544/pcd8544.py
import time
from functools import reduce

import numpy
from gpiozero import PWMLED, SPIDevice, DigitalOutputDevice
from PIL import Image, ImageDraw, ImageFont


class SysCommand(object):
    """Display control"""
    DISPLAY = 0x08
    """Function set"""
    FUNC = 0x20
    """Set Y address of RAM"""
    YADDR = 0x40
    """Set Y address of RAM"""
    XADDR = 0x80

    """Temperature control"""
    TEMP = 0x04
    """Bias system"""
    BIAS = 0x10
    """Set Vop"""
    VOP = 0x80


class Setting(object):
    """Sets display configuration"""
    DISPLAY_E = 0x01
    """Sets display configuration"""
    DISPLAY_D = 0x04

    """Extended instruction set"""
    FUNC_H = 0x01
    """Entry mode"""
    FUNC_V = 0x02
    """Power down control"""
    FUNC_PD = 0x04

    """Set bias system"""
    BIAS_BS0 = 0x01
    """Set bias system"""
    BIAS_BS1 = 0x02
    """Set bias system"""
    BIAS_BS2 = 0x04


class DisplaySize(object):
    WIDTH = 84
    HEIGHT = 48


class DisplayGraphics(object):

    """
    A Graphics implementation for any Display type usign Pillow
    """
    def __init__(self, display):
        """
        :param Display display:
        """
        self.display = display
        self.image = Image.new('1', (display.width, display.height))

        self.draw = ImageDraw.Draw(self.image)

    def clear(self):
        self.draw.rectangle([(0, 0), (self.display.width, self.display.height)], fill=0)

    def dispose(self):
        import time
        start_time1 = time.time()

        pixels = list(self.image.getdata())
        pixels = [pixels[i * self.display.width:(i + 1) * self.display.width] for i in range(self.display.height)]
        pixels_traspose = numpy.array(pixels).T

        concat = lambda result, lista: list(result) + list(lista)
        bits_to_byte = lambda byte, bit: int(byte << 1 | bit)

        pixels = reduce(concat, pixels_traspose, [])

        byte_size = 8

        pixels = [
            reduce(
                bits_to_byte,
                reversed(pixels[i * byte_size:(i + 1) * byte_size])
            )
            for i in range(int((self.display.height * self.display.width) / byte_size))
        ]

        self.display.write_all(pixels)

        print(" - Discover changes: %s seconds " % (time.time() - start_time1))

    def close(self):
        del self.draw
        del self.image

    def open(self, image):
        self.close()

        self.image = Image.open(image) \
            .crop((0, 0, self.display.width, self.display.height)) \
            .convert("1", colors=2)
            # .resize((self.display.width, self.display.height)) \

        self.draw = ImageDraw.Draw(self.image)


class PCD8544(SPIDevice):
    """
    PCD8544 display implementation.
    This implementation uses software shiftOut implementation?
    @author SrMouraSilva
    Based in 2013 Giacomo Trudu - wicker25[at]gmail[dot]com
    Based in 2010 Limor Fried, Adafruit Industries
          https://github.com/adafruit/Adafruit_Nokia_LCD/blob/master/Adafruit_Nokia_LCD/PCD8544.py
    Based in CORTEX-M3 version by Le Dang Dung, 2011 LeeDangDung@gmail.com (tested on LPC1769)
    Based in Raspberry Pi version by Andre Wussow, 2012, desk@binerry.de
    Based in Raspberry Pi Java version by Cleverson dos Santos Assis, 2013, tecinfcsa@yahoo.com.br
    https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/README.md
    The SPI master driver is disabled by default on Raspbian.
    To enable it, use raspi-config, or ensure the line
    dtparam=spi=on isn't commented out in /boot/config.txt, and reboot.
    :param int din: Serial data input
    :param int sclk: Serial clock input (clk)
    :param int dc: Data/Command mode select (d/c)
    :param int rst: External reset input (res)
    :param int cs: Chip Enable (CS/SS, sce)
    :param contrast
    :param inverse
    """
    def __init__(self, din, sclk, dc, rst, cs, contrast=60, inverse=False):
        super(PCD8544, self).__init__(clock_pin=sclk, mosi_pin=din, miso_pin=9, select_pin=cs)

        self.DC = DigitalOutputDevice(dc)
        self.RST = DigitalOutputDevice(rst)

        self._reset()
        self._init(contrast, inverse)

        self.drawer = DisplayGraphics(self)
        self.clear()
        self.dispose()

    def _reset(self):
        self.RST.off()
        time.sleep(0.100)
        self.RST.on()

    def _init(self, contrast, inverse):
        # H = 1
        self._send_command(SysCommand.FUNC | Setting.FUNC_H)
        self._send_command(SysCommand.BIAS | Setting.BIAS_BS2)
        self._send_command(SysCommand.VOP | contrast & 0x7f)
        # H = 0
        self._send_command(SysCommand.FUNC | Setting.FUNC_V)
        self._send_command(
            SysCommand.DISPLAY |
            Setting.DISPLAY_D |
            Setting.DISPLAY_E * (1 if inverse else 0)
        )

    def _send_command(self, data):
        self.DC.off()

        self._spi.write([data])

    def _send_data_byte(self, x, y, byte):
        self._set_cursor_x(x)
        self._set_cursor_y(y)

        self.DC.on()
        self._spi.write([byte])

    def set_contrast(self, value):
        self._send_command(SysCommand.FUNC | Setting.FUNC_H)
        self._send_command(SysCommand.VOP | value & 0x7f)
        self._send_command(SysCommand.FUNC | Setting.FUNC_V)

    def write_all(self, data):
        self._set_cursor_x(0)
        self._set_cursor_y(0)

        self.DC.on()
        self._spi.write(data)

    def _set_cursor_x(self, x):
        self._send_command(SysCommand.XADDR | x)

    def _set_cursor_y(self, y):
        self._send_command(SysCommand.YADDR | y)

    def clear(self):
        self._set_cursor_x(0)
        self._set_cursor_y(0)

        self.drawer.clear()

    @property
    def width(self):
        return DisplaySize.WIDTH

    @property
    def height(self):
        return DisplaySize.HEIGHT

    @property
    def value(self):
        return 0

    def close(self):
        super(PCD8544, self).close()

    @property
    def draw(self):
        return self.drawer.draw

    def dispose(self):
        self.drawer.dispose()


BORDER = 5
FONTSIZE = 10

display = PCD8544(din=10, sclk=11, dc=12, rst=24, cs=8)
# display = PCD8544(din=10, sclk=11, dc=6, rst=5, cs=8)
# bl = PWMLED(13)
# bl.value = True


def make_image(text):
    text = str(text)
    draw = display.draw
    # Draw a black background
    draw.rectangle((0, 0, display.width - 1, display.height - 1), outline=255, fill=0)

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


def show(text):
    make_image(text)
    display.dispose()


if __name__ == '__main__':
    show('3 2 3 2 1')
