# encoding: utf-8
"""
@author: Jiahao LU
@contact: lujiahao8146@gmail.com
@file: CmdUtil.py
@time: 2020/4/12
@desc:
"""
import ctypes,sys

STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

# Windows CMD命令行 字体颜色定义 text colors
# FOREGROUND_BLACK = 0x00 # black.
FOREGROUND_DARKBLUE = 0x01 # dark blue.
# FOREGROUND_DARKGREEN = 0x02 # dark green.
# FOREGROUND_DARKSKYBLUE = 0x03 # dark skyblue.
# FOREGROUND_DARKRED = 0x04 # dark red.
# FOREGROUND_DARKPINK = 0x05 # dark pink.
# FOREGROUND_DARKYELLOW = 0x06 # dark yellow.
# FOREGROUND_DARKWHITE = 0x07 # dark white.
FOREGROUND_DARKGRAY = 0x08 # dark gray.
FOREGROUND_BLUE = 0x09 # blue.
FOREGROUND_GREEN = 0x0a # green.
FOREGROUND_SKYBLUE = 0x0b # skyblue.
FOREGROUND_RED = 0x0c # red.
FOREGROUND_PINK = 0x0d # pink.
# FOREGROUND_YELLOW = 0x0e # yellow.
# FOREGROUND_WHITE = 0x0f # white.


# Windows CMD命令行 背景颜色定义 background colors
# BACKGROUND_BLUE = 0x10 # dark blue.
# BACKGROUND_GREEN = 0x20 # dark green.
# BACKGROUND_DARKSKYBLUE = 0x30 # dark skyblue.
# BACKGROUND_DARKRED = 0x40 # dark red.
# BACKGROUND_DARKPINK = 0x50 # dark pink.
# BACKGROUND_DARKYELLOW = 0x60 # dark yellow.
# BACKGROUND_DARKWHITE = 0x70 # dark white.
# BACKGROUND_DARKGRAY = 0x80 # dark gray.
# BACKGROUND_SKYBLUE = 0xb0 # skyblue.
# BACKGROUND_RED = 0xc0 # red.
# BACKGROUND_PINK = 0xd0 # pink.
# BACKGROUND_YELLOW = 0xe0 # yellow.
# BACKGROUND_WHITE = 0xf0 # white.
# get handle
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool

#reset white
def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

#sky blue
def printSkyBlue(mess):
    set_cmd_text_color(FOREGROUND_SKYBLUE)
    sys.stdout.write(mess.__str__() + '\n')
    resetColor()

#pink
def printPink(mess):
    set_cmd_text_color(FOREGROUND_PINK)
    sys.stdout.write(mess.__str__() + '\n')
    resetColor()

# 暗蓝色
# dark blue
def printDarkBlue(mess):
    set_cmd_text_color(FOREGROUND_DARKBLUE)
    sys.stdout.write(mess.__str__() + '\n')
    resetColor()
#dark white
def printDarkGray(mess):
    set_cmd_text_color(FOREGROUND_DARKGRAY)
    sys.stdout.write(mess.__str__() + '\n')
    resetColor()
