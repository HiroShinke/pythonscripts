

from subprocess import Popen, PIPE
import pty
import os
import sys
import tty
import termios
import fcntl
import array
import argparse

def setecho(fd,enable):
    attr = termios.tcgetattr(fd)
    if enable:
        attr[3] |= termios.ECHO
    else:
        attr[3] &= ~termios.ECHO
    termios.tcsetattr(fd,termios.TCSANOW,attr)

def convert_bytes(str):
    return str.encode().decode("unicode-escape").encode()
    
def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyseq")
    args = parser.parse_args()
    
    master, slave = pty.openpty()

    attrbk = termios.tcgetattr(sys.stdin.fileno())
    termios.tcsetattr(slave,termios.TCSANOW,attrbk)
    buf = array.array('h', [0, 0, 0, 0])
    fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, buf, True)
    fcntl.ioctl(slave, termios.TIOCSWINSZ, buf)
    setecho(slave,False)
    p = Popen(['vi'], stdin=slave, stdout=slave)

    attr = termios.tcgetattr(slave)
    os.close(slave)
    
    pid = os.fork()
    if pid == 0:
        while ret := os.read(master,1024):
            os.write(sys.stdout.fileno(),ret)

        os.close(master)
        os._exit(0)
            
    tty.setraw(sys.stdin.fileno())

    try:
        if args.keyseq:
            bytes = convert_bytes(args.keyseq)
            print(f"keyseq = {bytes}",file=sys.stderr)
            os.write(master,bytes)
    
        while ret := os.read(sys.stdin.fileno(),1024):
            os.write(master,ret)

    except Exception as e:
        pass
    
    os.close(master)
    ret = p.wait()

    termios.tcsetattr(sys.stdout.fileno(),termios.TCSANOW,attrbk)
                      

if __name__ == "__main__":
    main()

