# timed_quiz
A tiny CLI timed math quiz program in Python3.

Lixiang Luo

July, 2020

== Update July 13, 2020 ==
The code has ben completely rewritten using Python3, without any external dependencies. The only dependency is the assumption of a VT100-compatible terminal. The C version is no longer maintained.

Example screenshot:
```
26   PAUSED                      │$ tail -f history.txt
                                 │76 + 44 = 3   @
     87 + 30 = 117               │
                                 │>>> Sun Apr 19 13:44:20 2020
     CORRECT!                    │
                                 │98 + 17 = 115
Correct:    9                    │15 + 66 = 34   @
  Wrong:    3                    │73 + 33 = 106
    APM:   18                    │14 + 69 = 73   @
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

In this example, the quiz program and a separte shell showing the history record run in two tmux panes side-by-side. The quiz interface has a continuously running clock on the top-left corner, a question in the middle and the counts of correct and wrong answers so far at the bottom. APM (answers per minute) is calculated every 10 seconds. After entering each answer, "CORRECT!" or "WRONG!" shows up below the question. All the questions and answers are automatically appended to a file called "history.txt" in the current directory.

Example command line:
```
$ ./timed_quiz_new.py --timeout=20 --type=2 --x1lrange=8,10 --x2range=2,6
```

Use "-h" argument to check optional aruguments.

Additional controls:
* SPACE pauses the timer.
* Q quits the program immediately.

VT100 sequences are used to control terminal output, and Python threading is used to control the timer. All terminal output calls are guarded by a global mutex. The code should work with any Python3 environment on a VT100-compatible terminal.

Hope you find it useful!
