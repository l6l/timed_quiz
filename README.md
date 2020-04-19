# timed_quiz
A tiny terminal timed math quiz program using pthread and ncurses.

Lixiang Luo
April, 2020

Screenshot:
```
26   PAUSED                      │$ tail -f history.txt
                                 │76 + 44 = 3   @
     87 + 30 = 117               │
                                 │>>> Sun Apr 19 13:44:20 2020
     CORRECT!                    │
                                 │98 + 17 = 115
Correct:    9                    │15 + 66 = 34   @
  Wrong:    3                    │73 + 33 = 106
                                 │14 + 69 = 73   @
                                 │13 + 50 = 63
                                 │6 + 26 = 32
                                 │72 + 89 = 161
                                 │5 + 4 = 9
                                 │66 + 96 = 152   @
                                 │57 + 2 = 59
                                 │43 + 83 = 126
                                 │93 + 25 = 118
                                 │87 + 30 = 117
```

In this example, the quiz program and a separte shell showing the history record run in two tmux panes side-by-side. The quiz interface has a continuously running clock on the top-left corner, a question in the middle and the counts of correct and wrong answers so far at the bottom. After entering each answer, "CORRECT!" or "WRONG!" shows up below the question. All the questions and answers are automatically appended to a file called "history.txt" in the current directory.

The code is started with two arguments. The first is the total quiz time in seconds, and the second is the quiz range, which determines the range of random numbers to be used in the questions.

Additional controls:
* SPACE pauses the timer.
* Q quits the program immediately.

Ncurses is used to control terminal output, and pthread is used to control the timer. All ncurses output calls are guarded by a global mutex. The code is extremely simple and should work with most Unix-like environment, including Cygwin.

To build:
```
$ gcc -o run_quiz.x timed_quiz.c -lncurses -lpthread
```

Hope you find it useful!
