

from ctypes import *

GetLastError     = windll.kernel32.GetLastError
GMEM_MOVEABLE = 0x002
CF_TEXT        = 0x0001

def get_clipboard_bytes():
    text = ""
    if windll.user32.OpenClipboard(c_int(0)):
        h_clip_mem = windll.user32.GetClipboardData(1)
        windll.kernel32.GlobalLock.restype = c_char_p
        b = windll.kernel32.GlobalLock(c_int(h_clip_mem))
        windll.kernel32.GlobalUnlock(c_int(h_clip_mem))
        windll.user32.CloseClipboard()
    return b


def set_clipboard_text(s):

    btext = bytes(s,"cp932")
    length = len(btext)
    
    if windll.user32.OpenClipboard(c_int(0)):

        hglb = windll.kernel32.GlobalAlloc(GMEM_MOVEABLE,
                                           length + 1)

        windll.kernel32.GlobalLock.restype = c_void_p
        lpstr = windll.kernel32.GlobalLock(c_int(hglb))

        strp = cast(lpstr,POINTER(c_char))

        memmove(strp,btext,length)
        strp[length] = c_char(0)

        windll.user32.SetClipboardData(CF_TEXT,c_int(hglb))

        windll.kernel32.GlobalUnlock(c_int(hglb))
        windll.user32.CloseClipboard()


if __name__ == "__main__":

    b = get_clipboard_bytes()
    t = str(b,"cp932")

    print(f"t = {t}")
    
    lines = t.splitlines()
    lines = [ ">> " + l + "\r\n" for l in lines ]
    text = "".join(lines)

    set_clipboard_text(text)

