#!/bin/python3

import logging
import threading
import time
import sys

sec=None
lock=None

def timer_function(name):
    global sec
    global lock

    logging.debug("Thread %s: starting", name)

    while True:
        time.sleep(1)
        logging.debug(sec)
        sec=sec+1

        with lock:
            sys.stdout.write("\x1b7");     # save cursor position
            sys.stdout.write("\x1b[?25l"); # hide cursor
            sys.stdout.flush()             # take effect
            sys.stdout.write("\x1b[f");    # jump to top-left corner
            sys.stdout.write(str(sec));    # write time
            sys.stdout.write("\x1b8");     # restore cursor position
            sys.stdout.write("\x1b[?25h"); # show cursor
            sys.stdout.flush()             # take effect

    logging.debug("Thread %s: finishing", name)

if __name__ == "__main__":
    sec=0
    lock=threading.Lock()
    sys.stdout.write("\x1b[f\x1b[J") # clear screen

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    fdbg=logging.FileHandler('debug.log')
    fdbg.setLevel(logging.DEBUG)
    fdbg.setFormatter(logging.Formatter("%(asctime)s: %(message)s",'%H:%M:%S'))
    logger.addHandler(fdbg)

    logging.debug("======== Start ========")
    logging.debug("Main    : before creating thread")
    x = threading.Thread(target=timer_function, args=(1,), daemon=True)
    logging.debug("Main    : before running thread")
    logging.debug("Main    : wait for the thread to finish")
    # x.join()
    sys.stdout.write ("\x1b[f\x1b[3B")
    sys.stdout.write ("Enter a number:\n")
    x.start()
    test_text = input ()
    test_number = int(test_text)
    sys.stdout.write ("The number you entered is: "+str(test_number) )

    logging.debug("Main    : all done")
