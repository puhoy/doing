
import argparse
from .cli import print_days, cmd_git, cmd_finish, add_task, cmd_touch

import logging


def main(args=None):
    parser = argparse.ArgumentParser(description="track what youre doing. tag with + or #")
    parser.add_argument("task",
                        help="what i am doing", nargs='*')
    parser.add_argument("-f", "--finish",
                        help="set finish time for task.\ndefaults to the 'last' task, may be time or date of task\n 'all' finishes all of today'",
                        nargs='?', const='last')
    parser.add_argument("--git",
                        help="calls git with the arguments you give (runs in ~/.doing)", nargs='+')
    parser.add_argument("--days",
                        help="prints a number of days or this 'month'.")
    parser.add_argument("--tags",
                        help="restrict prints to tasks with tags", nargs='+')
    parser.add_argument("--touch",
                        help="try to merge messages for this host, trigger a git commit", action='store_true')
    parser.add_argument("--debug",
                        help=argparse.SUPPRESS, action='store_true')

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.ERROR)

    if args.days:
        print_days(args.days, args.tags)

    elif args.git:
        cmd_git(args.git)

    elif args.task:
        if args.finish:
            add_task(' '.join(args.task), finish=True)
        else:
            add_task(' '.join(args.task))

    elif args.finish:
        cmd_finish(args.finish)

    elif args.touch:
        cmd_touch()

    else:
        print_days('today', args.tags)

if __name__ == "__main__":
    main()
