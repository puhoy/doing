
import argparse
from doing.cli import print_days, cmd_git, cmd_finish, add_task

import logging

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
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

    args = parser.parse_args()

    if args.days:
        print_days(args.days, args.tags)

    elif args.git:
        cmd_git(args.git)

    elif args.finish:
        cmd_finish(args.finish)

    elif args.task:
        add_task(' '.join(args.task))

    else:
        print_days('today', args.tags)