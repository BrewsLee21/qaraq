import curses

from utils import print_to_log_file

def main(stdscr):
    key = stdscr.getch()

    print_to_log_file(str(key))

curses.wrapper(main)
