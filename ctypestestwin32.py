# -*- coding: cp932 -*-

import pathlib
import argparse
import re

from ctypes import *
import ctypes

FindWindowEx = windll.user32.FindWindowExW
MessageBox   = windll.user32.MessageBoxW
SendMessage  = windll.user32.SendMessageW
GetLastError = windll.kernel32.GetLastError
EnumWindows  = windll.user32.EnumWindows
GetWindowText = windll.user32.GetWindowTextW
GetWindowTextLength = windll.user32.GetWindowTextLengthW

GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId
TerminateProcess         = windll.kernel32.TerminateProcess
OpenProcess              = windll.kernel32.OpenProcess


WNDENUMPROC = WINFUNCTYPE(c_bool, POINTER(c_int), POINTER(c_int))
ghwnd = None

def main():
    print(f"argtypes = {MessageBox.argtypes}")
    MessageBox(None,"Hello","Hello ctypes",0)
    EnumWindows(WNDENUMPROC(EnumWindowsProc), 0)


def EnumWindowsProc(hwnd, lParam):
    global ghwnd
    length = GetWindowTextLength(hwnd)
    buff = create_unicode_buffer(length + 1)
    GetWindowText(hwnd, buff, length + 1)
    if not re.search(r"IME",buff.value):
        print(f"{hwnd} {length} {buff.value}")
    return True

if __name__ == "__main__":
    main()

