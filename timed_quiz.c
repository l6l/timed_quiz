#include <stdlib.h>
#include <stdio.h>
#include <ncurses.h>
#include <unistd.h>
#include <pthread.h>
#include <time.h>

int clockx = 0;
int clocky = 0;
int sec_elapsed = 0;
int sec_inc = 1;
int quiz_timeout=10;

WINDOW * mainwin;
pthread_mutex_t nc_out_mutex;

void *run_clock (void *v)
{
  int x,y;

  while (sec_elapsed<quiz_timeout)
  {
    pthread_mutex_lock(&nc_out_mutex);
    getyx (mainwin,y,x);
    mvprintw (0,0,"%-4d",sec_elapsed);
    move (y,x);
    refresh ();
    pthread_mutex_unlock(&nc_out_mutex);
    sleep (1);

    sec_elapsed += sec_inc;
  }

  pthread_mutex_lock(&nc_out_mutex);
  getyx ((WINDOW*)mainwin,y,x);
  mvaddstr (clocky,clockx,"Timeout!");
  move (y,x);
  refresh ();
  pthread_mutex_unlock(&nc_out_mutex);

  return 0;
}

int main(int argc, char *argv[])
{
  /* ncurses init */
  int range;

  if (argc<2)
  {
    quiz_timeout=60;
  }
  else
  {
    sscanf(argv[1],"%d",&quiz_timeout);
    if (quiz_timeout<10 || quiz_timeout>300)
    {
      fprintf(stderr, "Timeout must be [10,300]\n");
      exit(EXIT_FAILURE);
    }
  }

  if (argc>=3)
  {
    sscanf(argv[2],"%d",&range);
  }
  else
  {
    range = 100;
  }
  range++;


  if ( (mainwin = initscr()) == NULL ) {
    fprintf(stderr, "Error initialising ncurses.\n");
    exit(EXIT_FAILURE);
  }

  clear ();
  noecho ();
  cbreak ();
  refresh ();
  usleep(10000);
  //keypad (stdscr, TRUE);

  char str[80];
  int c_right,c_wrong;
  int x1, x2, result;
  int p_m;
  int ans;
  int len;
  char newchar;
  int x0,y0;
  FILE *myfile;

  myfile = fopen("history.txt","a");

  srand(time(NULL));
  c_right = 0;
  c_wrong = 0;

  time_t now = time(0);
  fprintf(myfile,"\n>>> %s\n",ctime(&now));

  //mvaddstr(2, 5, " "); // required, otherwise wrong cursor location
  mvaddstr(6,0,"Correct:    0\n  Wrong:    0");
  refresh ();
  // start the timer
  pthread_t thread;
  pthread_create ( &thread, NULL, &run_clock, NULL );

  while ( sec_elapsed<quiz_timeout )
  {
    x1 = rand()%range; x2 = rand()%range;
    p_m = rand()%3-1>0?1:-1;

    if (p_m<0 && x1<x2)
    {
      result=x1; x1=x2; x2=result;
    }
    result = x1+p_m*x2;

    len = 0;

    pthread_mutex_lock(&nc_out_mutex);
    flushinp();
    mvaddstr(2, 5, "                          ");
    mvprintw(2, 5, "%d %c %d = ", x1, (p_m>0?'+':'-'), x2 );
    getyx(mainwin,y0,x0);
    refresh();
    pthread_mutex_unlock(&nc_out_mutex);

    curs_set(1);

    while (1)
    {
      newchar=getch();

      if ( newchar == 'Q' )
      {
        // TODO: terminate the timer thread properly
        goto finalize;
      }
      else if ( newchar==' ' )  // pause
      {
        pthread_mutex_lock(&nc_out_mutex);
        if (sec_inc==0)
        {
          mvaddstr(0,5,"       ");
          sec_inc=1;
        }
        else
        {
          mvaddstr(0,5,"PAUSED");
          sec_inc=0;
        }
        move(y0,x0+len);
        pthread_mutex_unlock(&nc_out_mutex);
      }
      else if ( len<8 && newchar>='0' && newchar<='9')
      {
        pthread_mutex_lock(&nc_out_mutex);
        mvaddch(y0,x0+len,newchar);
        pthread_mutex_unlock(&nc_out_mutex);
        str[len] = newchar;
        len++;
      }
      else if (len>0)
      {
        if ( newchar==10 ) break;  // ENTER
        else if ( newchar == 127 ) // BACKSPACE
        {
          len--;
          pthread_mutex_lock(&nc_out_mutex);
          mvaddch(y0,x0+len,' ');
          move(y0,x0+len);
          pthread_mutex_unlock(&nc_out_mutex);
        }
      }
    }

    curs_set(0);

    str[len]=0;
    sscanf(str,"%d",&ans);

    pthread_mutex_lock(&nc_out_mutex);
    if (ans==result)
    {
      mvaddstr(4, 5, "CORRECT!");
      c_right++;
    }
    else
    {
      mvaddstr(4, 5, "WRONG!  ");
      c_wrong++;
    }
    refresh ();
    pthread_mutex_unlock(&nc_out_mutex);

    fprintf(myfile,"%d + %d = %d %s\n",x1,x2,ans,(x1+x2==ans?" ":"  @"));
    fflush(myfile);

    getch();

    pthread_mutex_lock(&nc_out_mutex);
    mvaddstr(4, 5, "         ");
    mvprintw(6,0,"Correct: %4d\n  Wrong: %4d",c_right,c_wrong);
    refresh();
    pthread_mutex_unlock(&nc_out_mutex);
  }

  curs_set (1);
  getch();

finalize:

  echo ();
  nocbreak ();

  delwin (mainwin);
  endwin ();
  refresh ();

  fclose(myfile);

  return EXIT_SUCCESS;
}
