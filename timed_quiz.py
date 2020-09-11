#!/usr/bin/python3

# imports {{{
import logging
import threading
import time
import datetime
import sys
import tty, termios
import random
import argparse
import atexit
# }}}

##################    Global stuff    ################## {{{
x0 = 0
y0 = 0
sec = 0
sec_inc = 1
lock=threading.Lock()
# Set up unbuffered read from stdin
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
flog = open('history.txt','a')

# Set up logger output
logger = logging.getLogger()
fdbg=logging.FileHandler('debug.log')
fdbg.setLevel(logging.DEBUG)
fdbg.setFormatter(logging.Formatter("%(asctime)s: %(message)s",'%H:%M:%S'))
logger.addHandler(fdbg)
#}}}

##################     Functions      ################## {{{

def myclrline(y,x): #{{{
    with lock:
        sys.stdout.write ("\x1b[s\x1b[?25l")
        sys.stdout.flush ()
        sys.stdout.write ("\x1b["+str(y+y0)+";"+str(x+x0)+"H\x1b[K\x1b[u\x1b[?25h")
        sys.stdout.flush ()
#}}}

def myaddstr(y,x,buf): #{{{
    with lock:
        sys.stdout.write ("\x1b[s\x1b[?25l")
        sys.stdout.flush ()
        sys.stdout.write ("\x1b["+str(y+y0)+";"+str(x+x0)+"H"+buf+"\x1b[u\x1b[?25h")
        sys.stdout.flush ()
#}}}

def myaddstr_m(yxbuf): #{{{
    with lock:
        for i in yxbuf:
            sys.stdout.write ("\x1b[s\x1b[?25l")
            sys.stdout.flush ()
            sys.stdout.write ("\x1b["+str(i[0]+y0)+";"+str(i[1]+x0)+"H"+i[2]+"\x1b[u\x1b[?25h")
            sys.stdout.flush ()
#}}}

def timer_function(name): #{{{
    global sec
    global lock

    logging.debug ("Thread %s: starting", name)

    while sec<quiz_timeout:
        time.sleep(1)
        logging.debug (sec)
        sec = sec + sec_inc
        towrite = [(1-y0, 1-x0, "\x1b[2m"+str(sec)+"\x1b[m")];
        if sec % 5 == 1:
            towrite.append ((10,10,str(int((c_right+c_wrong)*60./sec))+"  "));
        myaddstr_m (towrite)

    myaddstr (1-y0, 1-x0, "\x1b[2m"+str(sec)+"\x1b[m  TIMEOUT!")

    logging.debug ("Thread %s: finishing", name)
#}}}

def cleanup(): #{{{
    sys.stdout.write("\x1bc\x1b[?25h\x1b[f\x1b[J") # clear screen
    sys.stdout.flush ()
    termios.tcsetattr (fd, termios.TCSADRAIN, old_settings)
    logging.debug ("Main    : all done")
    flog.close ()
#}}}

def _get_termsize(): #{{{
    import struct
    import fcntl
    cr = struct.unpack('hh',fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
    return cr  # (rows,columns)
#}}}

##################    Main program    ##################

parser = argparse.ArgumentParser(description="Fun math quiz for kids!")

parser.add_argument('-T','--timeout', type=int, default=10, help='timeout in seconds (default=10)')
parser.add_argument('-t','--type',    type=int, default=1, help='quiz type (1:add,2:sub,3:add+sub,default=1)')
parser.add_argument('-r1', '--x1range', type=str, default='0,10', help='x1 range')
parser.add_argument('-r2', '--x2range', type=str, default='0,10', help='x2 range')
parser.add_argument('--log', choices=['INFO','info','DEBUG','debug'], default='INFO', help='log level (default=INFO)')

try:
    options = parser.parse_args(sys.argv[1:])
except:
    print("Error parsing arguments!");
    sys.exit()

numeric_level = getattr(logging, options.log.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
logger.setLevel(numeric_level)

quiz_timeout = options.timeout

lower1,upper1  = options.x1range.split(',')
lower2,upper2  = options.x2range.split(',')
lower1 = int(lower1)
upper1 = int(upper1)
lower2 = int(lower2)
upper2 = int(upper2)

if options.type == 1: # sub
    q_type = 2
elif options.type == 2: # add/sub
    q_type = 3
else:
    q_type = 1  # add

# Proper TTY reset at exit
atexit.register (cleanup)

# TTY fullscreen and unbuffered input
tty.setraw (sys.stdin.fileno())
sys.stdout.write ("\x1b[f\x1b[J") # clear screen
sys.stdout.flush ()

(nrow,ncol) = _get_termsize ()
#flog.write(str(nrow/2-5)+" "+str(ncol))
x0 = max(int(ncol/2-8),0)
y0 = max(int(nrow/2-5),0)


# main quiz codes
flog.write("\n======== "+str(datetime.datetime.now())+" ========\n\n")

s = ""
sec = 0
c_right = 0
c_wrong = 0
signchar = ('-','+')

myaddstr_m ((( 1-y0,1-x0,"\x1b[2m0\x1b[m"),\
             ( 8,1,"Correct: 0"),\
             ( 9,1,"  Wrong: 0"),\
             (10,1,"    APM: 0")))

timer_thread = threading.Thread(target=timer_function, args=(1,), daemon=True)
timer_thread.start()

# Main loop over questions {{{
while sec < quiz_timeout:

    inplen = 0
    inpstr = [' ' for i in range(10)]

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

    t0 = datetime.datetime.now ()

    with lock:
        sys.stdout.write ("\x1b["+str(3+y0)+";"+str(3+x0)+"H"+ \
          str(x1) +" "+ signchar[p_m] +" "+ str(x2) +" = "+ \
          "\x1b[K\x1b[?25h") # clear line, show cursor
        sys.stdout.flush ()

    # Input processing loop {{{
    while True:

        # Read 1 character
        newchar = sys.stdin.read(1)

        if newchar == 'Q':   # immediately quit
            sys.exit ()

        elif newchar == ' ':  # toggle pause
            if sec_inc == 0:
                myclrline (1,5)
                sec_inc = 1
            else:
                myaddstr (1,5,"PAUSED")
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
                    sys.stdout.write ("\x1b[D\x1b[K")
                    sys.stdout.flush ()
    # END input processing loop}}}

    logging.debug (inpstr)
    ans = int(s.join(inpstr[0:inplen]))

    if ans == result:
        myaddstr(5, 3, "\x1b[32mCORRECT!\x1b[m");
        c_right = c_right + 1
        markchar = ' '
    else:
        myaddstr(5, 3, "\x1b[91mWRONG!  \x1b[m");
        c_wrong = c_wrong + 1
        markchar = '@'

    td = datetime.datetime.now() - t0

    flog.write( "%1s %3d    %d %s %d = %d\n" % \
      ( markchar, int(td.total_seconds()), x1, signchar[p_m], x2, ans ) )

    newchar = sys.stdin.read(1)

    myclrline (5,3);
    myaddstr_m ((( 8,10,str(c_right)),
                 ( 9,10,str(c_wrong))));

# END question loop }}}

newchar = sys.stdin.read(1)
