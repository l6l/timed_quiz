#!/bin/python3

import logging
import threading
import time
import sys
import tty, termios
import random
import datetime
import argparse
import atexit

sec=0
sec_inc=1
lock=None
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
tty.setraw(sys.stdin.fileno())

def myclrline(y,x):
    with lock:
        sys.stdout.write("\x1b7\x1b[?25l"); # save cursor position and hide it
        sys.stdout.flush()
        sys.stdout.write("\x1b["+str(y)+";"+str(x)+"H");    # jump
        sys.stdout.write("\x1b[K\x1b8\x1b[?25h");    # clear line, restore cursor position and show it
        sys.stdout.flush()             # take effect

def myaddstr(y,x,buf):
    with lock:
        sys.stdout.write("\x1b7");     # save cursor position
        sys.stdout.write("\x1b[?25l"); # hide cursor
        sys.stdout.flush()             # take effect
        sys.stdout.write("\x1b["+str(y)+";"+str(x)+"H");    # jump
        sys.stdout.write(buf);         # write buf
        sys.stdout.write("\x1b8");     # restore cursor position
        sys.stdout.write("\x1b[?25h"); # show cursor
        sys.stdout.flush()             # take effect

def timer_function(name):
    global sec
    global lock

    logging.debug("Thread %s: starting", name)

    while True:
        time.sleep(1)
        logging.debug(sec)
        sec = sec + sec_inc
        myaddstr(0,0,str(sec));

    logging.debug("Thread %s: finishing", name)


def cleanup():
    sys.stdout.write("\x1bc\x1b[?25h\x1b[f\x1b[J") # clear screen
    sys.stdout.flush ()
    termios.tcsetattr (fd, termios.TCSADRAIN, old_settings)
    logging.debug("Main    : all done")


if __name__ == "__main__":

    atexit.register (cleanup)
    parser = argparse.ArgumentParser(description="Parses command.")

    parser.add_argument("-T", "--timeout", type=int, default=10, help="timeout in seconds")
    parser.add_argument("-t", "--type", type=int, default=1, help="quiz type")
    parser.add_argument("-X1L", "--x1lower", type=int, default=0, help="x1 lower bound")
    parser.add_argument("-X1U", "--x1upper", type=int, default=10, help="x1 upper bound")
    parser.add_argument("-X2L", "--x2lower", type=int, default=0, help="x2 lower bound")
    parser.add_argument("-X2U", "--x2upper", type=int, default=10, help="x2 upper bound")

    options = parser.parse_args(sys.argv[1:])

    quiz_timeout = options.timeout
    lower1 = options.x1lower
    upper1 = options.x1upper
    lower2 = options.x2lower
    upper2 = options.x2upper

    if options.type == 1: # sub
        q_type = 2
    elif options.type == 2: # add/sub
        q_type = 3
    else:
        q_type = 1  # add

    s = ""
    sec = 0
    inplen = 0
    inpstr = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
    c_right = 0
    c_wrong = 0
    signchar = ('-','+')
    lock=threading.Lock()

    sys.stdout.write("\x1b[f\x1b[J") # clear screen

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    flog=logging.FileHandler('history.log')
    flog.setLevel(logging.INFO)
    flog.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(flog)

    fdbg=logging.FileHandler('debug.log')
    #fdbg.setLevel(logging.DEBUG)
    fdbg.setFormatter(logging.Formatter("%(asctime)s: %(message)s",'%H:%M:%S'))
    logger.addHandler(fdbg)

    logging.info("\n======== "+str(datetime.datetime.now())+" ========")
    logging.debug("Main    : before creating thread")
    x = threading.Thread(target=timer_function, args=(1,), daemon=True)
    logging.debug("Main    : before running thread")

    myaddstr(1,1,"0")
    myaddstr(7,1,"Correct: 0")
    myaddstr(8,1,"  Wrong: 0")

    x.start()

    while sec < quiz_timeout:

        t0 = datetime.datetime.now()

        x1 = random.randint(lower1,upper1)
        x2 = random.randint(lower2,upper2)

        if q_type == 1:
            p_m = 1
        elif q_type == 2:
            p_m = 0
        elif q_type == 3:
            p_m = random.randint(0,1)

        if p_m == 0:
            if x1 < x2:
                tv = x1
                x1 = x2
                x2 = tv
            result = x1 - x2
        else:
            result = x1 + x2

        inplen = 0

        with lock:
            sys.stdout.write("\x1b[3;6H");    # jump
            sys.stdout.write(str(x1) + " " + signchar[p_m] + " " + str(x2) + " = ")
            sys.stdout.write("\x1b[K\x1b[?25h"); # clear line, show cursor
            sys.stdout.flush()

        while True:

            newchar = sys.stdin.read(1)

            if newchar == 'Q':
                sys.exit ()

            elif newchar == ' ':
                if sec_inc == 0:
                    myclrline(0,5)
                    sec_inc = 1
                else:
                    myaddstr(0,5,"PAUSED")
                    sec_inc = 0

            elif inplen<8 and newchar>='0' and newchar<='9':
                inpstr[inplen] = newchar
                inplen = inplen + 1
                with lock:
                    sys.stdout.write (newchar)
                    sys.stdout.flush ()

            elif inplen>0:
                #logging.debug("Main    : unknown character"+str(ord(newchar)))
                if ord(newchar) == 13:     # ENTER
                    break
                elif ord(newchar) == 127:  # BACKSPACE
                    inplen = inplen - 1
                    with lock:
                        sys.stdout.write ("\x1b[1D\x1b[K")
                        sys.stdout.flush ()

        logging.debug(inpstr)
        ans = int(s.join(inpstr))

        if ans == result:
            myaddstr(5, 6, "CORRECT!");
            c_right = c_right + 1
            markchar = ' '
        else:
            myaddstr(5, 6, "WRONG!  ");
            c_wrong = c_wrong + 1
            markchar = '@'

        td = datetime.datetime.now() - t0

        logging.info( str(x1) + " " + signchar[p_m] + " " + str(x2) + " = " \
            + str(result) + " " + markchar + " " + str(int(td.total_seconds())) )

        newchar = sys.stdin.read(1)

        myclrline(5,6);
        myaddstr(7,1,"Correct: "+str(c_right));
        myaddstr(8,1,"  Wrong: "+str(c_wrong));


