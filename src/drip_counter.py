

import sys
import select
import time
import os

from calibrate.drip_detector import DripDetector

class _Getch:
    """Gets a single character from standard input.  Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


def main():
    print("Listening for drips press any key to stop")
    drip_detector = DripDetector(1, echo_drips=True)
    try:
        drip_detector.start()
        while (not getch()):
            time.sleep(0.1)
        drip_detector.stop()
    except KeyboardInterrupt:
        drip_detector.stop()

if __name__ == "__main__":
    main()