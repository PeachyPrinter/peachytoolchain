

import sys
import select
import time
from calibrate.drip_detector import DripDetector

def heardEnter():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return True
    return False

def main():
    print("Listening for drips Press Enter to stop")
    drip_detector = DripDetector(1, echo_drips=True)
    drip_detector.start()

    while (not heardEnter()):
        time.sleep(0.1)

    drip_detector.stop()

if __name__ == "__main__":
    main()