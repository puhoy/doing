import argparse
import logging
import humanize
import datetime
from doing.helpers import colorize, get_uptime
from doing import time_format, date_format, hostname
from doing.git import git

logging.basicConfig(level=logging.ERROR)

def cmd_git(args):

    git_args = []
    for arg in args:
        git_args += arg.split()

    git(git_args)


def print_datapoint(point, with_timestamp=False):
    if with_timestamp:
        print(
            colorize('bold',
                     '@%s  ' % int(point.time) + datetime.datetime.fromtimestamp(point.time).strftime(time_format)))
    else:
        print(colorize('bold', '  ' + datetime.datetime.fromtimestamp(point.time).strftime(time_format)))
    print('    ' + point.task)
    print('    pc was up for %s\n' % humanize.naturaldelta(point.uptime))


def print_day(day, tags):
    # bold, underlined date
    print(colorize('bold', colorize('underline', '%s' % (day.day.strftime(date_format + ' (%A)')))))
    if not day.datapoints:
        print('nothing done.\n')

    for host in day.datapoints.keys():
        print('on %s' % host)
        boot_time = datetime.datetime.fromtimestamp(day.datapoints[host][0].time) - datetime.timedelta(seconds=day.datapoints[host][0].uptime)
        print(colorize('bold', '[boot] %s\n' % boot_time.strftime(time_format)))
        for point in day.datapoints[host]:
            if tags:
                tag_found = False
                #print(point.__dict__.keys())
                for tag in point.__dict__.get('tags', []):
                    print(tag)
                    if tag in tags:
                        tag_found = True
                if tag_found:
                    print_datapoint(point)
            else:
                print_datapoint(point)
        if day.day.date() == datetime.datetime.today().date():
            print(colorize('bold', '\nup for %s now.' % humanize.naturaldelta(get_uptime())))


def print_days(days, tags):
    from doing.models import Day
    from doing.helpers import get_last_days

    if tags:
        print('(only tasks with %s)' % tags)

    days_to_print = []
    if days.lower() in ['today', '']:
        days_to_print = [Day('today')]
    elif days.lower() in ['month']:
        number_of_days = datetime.date.today().day
        days_to_print = get_last_days(number_of_days)
    else:
        try:
            number_of_days = int(days)
            days_to_print = get_last_days(number_of_days)

            pass  # print_days(days)
        except ValueError:
            print("unknown argument %s. --days takes 'month' or a number of days. " % args.days)

    for day in days_to_print:
        print_day(day, tags)


def cmd_finish(args):
    from doing.models import Day
    from doing import time_format, hostname
    import datetime

    if args == 'last':
        d = Day('today', hostname)
        try:
            if d.datapoints[hostname]:
                last_point = d.datapoints[hostname][-1]
                if last_point.__dict__.get('finished', False):
                    print(
                        'task "%s" \nalready finished (@%s)' % (
                        last_point.task, datetime.datetime.fromtimestamp(last_point.finished).strftime(time_format)))
                    return
                last_point.finish()
                d.write()
                fin_time = datetime.datetime.fromtimestamp(last_point.finished)
                start_time = datetime.datetime.fromtimestamp(last_point.time)
                print('task "%s" \nfinished @%s (took %s)' % (
                    last_point.task,
                    fin_time.strftime(time_format),
                    humanize.naturaldelta(fin_time - start_time)
                ))
            else:
                print('sorry, no last task to finish for today.')
        except Exception as e:
            logging.error('could not finish last task.', e)
        exit(0)

    elif args == 'all':
        print('TODO all')
        exit(0)
    else:
        try:
            # check if its our time format (means search in today)
            timevals = args.finish.split(':')
            d = datetime.datetime.today().replace(hour=timevals[0], minute=timevals[1], second=timevals[2])
            stamp = d.timestamp()
        except ValueError:
            # no? then check if its our date format
            try:
                stamp = datetime.strptime(args.finish, date_format).timestamp()
            except ValueError:
                stamp = None


def add_task(task):
    from doing.models import Day
    from doing.git import folder_is_git_tracked
    day = Day('today', hostname=hostname)
    day.add_task(task)
    print('added')
    print_datapoint(day.datapoints[hostname][-1])

    if folder_is_git_tracked():
        git(['add', '-A'])
        git(['commit', '-m', '"%s - %s"' % ('autocommit', task)])

    pass


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
