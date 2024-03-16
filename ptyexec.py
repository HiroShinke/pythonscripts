

from subprocess import Popen, PIPE
import pty
import os
import sys
import tty
import termios
import fcntl
import array
import argparse
import re
import signal

def setecho(fd,enable):
    attr = termios.tcgetattr(fd)
    if enable:
        attr[3] |= termios.ECHO
    else:
        attr[3] &= ~termios.ECHO
    termios.tcsetattr(fd,termios.TCSANOW,attr)

def convert_bytes(str):
    return str.encode().decode("unicode-escape").encode()

def handler(signal,frame):
    # print("Sub Porcess exit",file=sys.stderr)
    raise InterruptedError()

def pty_exec(cmd,keyseq=None):

    args = re.split(r"\s+",cmd)
    
    master, slave = pty.openpty()

    attrbk = termios.tcgetattr(sys.stdin.fileno())
    termios.tcsetattr(slave,termios.TCSANOW,attrbk)
    buf = array.array('h', [0, 0, 0, 0])
    fcntl.ioctl(sys.stdin.fileno(), termios.TIOCGWINSZ, buf, True)
    fcntl.ioctl(slave, termios.TIOCSWINSZ, buf)
    setecho(slave,False)
    p = Popen(args, stdin=slave, stdout=slave)

    attr = termios.tcgetattr(slave)
    os.close(slave)
    
    pid = os.fork()
    if pid == 0:
        while ret := os.read(master,1024):
            os.write(sys.stdout.fileno(),ret)

        os.close(master)
        os.kill(os.getppid(),signal.SIGTERM)
        os._exit(0)
            
    tty.setraw(sys.stdin.fileno())
    signal.signal(signal.SIGTERM,handler)
    
    try:
        if keyseq:
            print(f"keyseq = {bytes}",file=sys.stderr)
            os.write(master,keyseq)
    
        while ret := os.read(sys.stdin.fileno(),1024):
            os.write(master,ret)

    except InterruptedError:
        pass
    
    os.close(master)
    ret = p.wait()

    termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,attrbk)
    

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyseq")
    parser.add_argument("--cmd")
    args = parser.parse_args()

    if args.keyseq:
        keyseq = convert_bytes(args.keyseq)
    else:
        keyseq = None

    pty_exec(args.cmd,keyseq)
    

if __name__ == "__main__":
    main()

