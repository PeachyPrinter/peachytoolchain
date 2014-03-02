

import sys
import select
import time
import os
import termios
import fcntl

from calibrate.drip_detector import DripDetector

def getch():
  fd = sys.stdin.fileno()

  oldterm = termios.tcgetattr(fd)
  newattr = termios.tcgetattr(fd)
  newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
  termios.tcsetattr(fd, termios.TCSANOW, newattr)

  oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

  try:        
    while 1:            
      try:
        c = sys.stdin.read(1)
        break
      except IOError: pass
  finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  return c

def main():
    print("Listening for drips Press Enter to stop")
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