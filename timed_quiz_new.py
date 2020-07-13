#!/bin/python3

import logging
import threading
import time
import sys
import tty, termios

sec=0
sec_inc=1
lock=None

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

if __name__ == "__main__":

    s = ""
    sec = 0
    inplen = 0
    inpstr = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
    c_right = 0
    c_wrong = 0
    lock=threading.Lock()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setraw(sys.stdin.fileno())

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
    # x.join()

    myaddstr(7,1,"Correct: 0");
    myaddstr(8,1,"  Wrong: 0");

    x.start()

    while sec < 10:

        x1 = sec + 2
        x2 = sec * 2 + 3
        p_m = 1
        result = x1 + p_m * x2

        inplen = 0

        with lock:
            sys.stdout.write("\x1b[3;6H");    # jump
            sys.stdout.write(str(x1) + " + " + str(x2) + " = ")
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
        else:
            myaddstr(5, 6, "WRONG!  ");
            c_wrong = c_wrong + 1

        newchar = sys.stdin.read(1)

        myaddstr(7,1,"Correct: "+str(c_right));
        myaddstr(8,1,"  Wrong: "+str(c_wrong));


    termios.tcsetattr (fd, termios.TCSADRAIN, old_settings)

    #test_number = int(test_text)
    #sys.stdout.write ("The number you entered is: " + s.join(inpstr))

    logging.debug("Main    : all done")
