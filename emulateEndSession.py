# -*- coding: cp932 -*-

import pathlib
import argparse

from ctypes import *

FindWindowEx = windll.user32.FindWindowExW
SendMessage  = windll.user32.SendMessageW
GetWindowThreadProcessId = windll.user32.GetWindowThreadProcessId

GetLastError     = windll.kernel32.GetLastError
OpenProcess      = windll.kernel32.OpenProcess
TerminateProcess = windll.kernel32.TerminateProcess


WM_QUERYENDSESSION = 0x0011
WM_ENDSESSION = 0x0016

PROCESS_TERMINATE = 0x01

def main():

    hWnd = FindWindowEx(None,None,None,"漢字.txt - メモ帳")
    print(f"{hWnd}")
    if not hWnd:
        n = GetLastError()
        raise ValueError(f"window not found: {n}")

    processIdBuff = create_string_buffer(4)
    tid = GetWindowThreadProcessId(hWnd,processIdBuff)
    processId = int.from_bytes(processIdBuff.raw,"little")
    print(f"processId = {processId}")
    print(f"threadId  = {tid}")    
    hProcess = OpenProcess(PROCESS_TERMINATE,0,processId)
    n = GetLastError()
    print(f"LastError {n}")

    wParam = create_string_buffer(2)
    lParam = create_string_buffer(4)
    lParam.raw = int.to_bytes(1,4,"little")
    ret = SendMessage(hWnd,WM_QUERYENDSESSION,wParam,lParam)
    print(f"QUERYENDSESSION = {ret}")

    wParam.raw = int.to_bytes(ret,2,"little")
    lParam.raw = int.to_bytes(1,4,"little")
    ret = SendMessage(hWnd,WM_ENDSESSION,wParam,lParam)
    print(f"ENDSESSION = {ret}")

    TerminateProcess(hProcess,0)
    n = GetLastError()
    print(f"LastError {n}")


if __name__ == "__main__":
    main()

