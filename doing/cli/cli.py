import logging
import humanize
import datetime
from ..helpers import get_uptime, try_parse_time
from ..cli.colorize import colorize
from .. import time_format, date_format, hostname
from ..git import git
from doing.helpers import touch
from doing.git import folder_is_git_tracked
from .unicode_icons import icon
from textwrap import indent, fill, wrap, TextWrapper


def cmd_git(args):
    git_args = []
    for arg in args:
        git_args += arg.split()

    git(git_args)


def print_datapoint(point, base_indent=' '):
    textblock = []
    this_indent = base_indent + '  '
    if point.__dict__.get('finished', False):
        iprint(
            colorize(['bold', 'okgreen'],
                     datetime.datetime.fromtimestamp(point.time).strftime(time_format)), base_indent)

        iprint(colorize(['bold', 'okgreen'],
                        '%s %s on %s ' % (
                            icon.check,
                            datetime.datetime.fromtimestamp(point.finished['time']).strftime(time_format),
                            point.finished['host'])), base_indent)
    else:
        iprint(colorize('bold', datetime.datetime.fromtimestamp(point.time).strftime(time_format)), base_indent)

    iprint(point.task, this_indent)
    iprint('pc was up for %s\n' % humanize.naturaldelta(point.uptime), this_indent)


def iprint(text, ind):
    for line in text.split('\n'):
        if line == '':
            print('')
        else:
            for l in wrap(line, width=70):
                print(indent(l, ind))


def print_day(day, tags, base_indent=' '):
    # bold, underlined date
    this_indent = base_indent + '  '

    iprint(colorize('bold', colorize('underline', '%s' % (day.day.strftime(date_format + ' (%A)')))), base_indent)
    if not day.datapoints:
        iprint('nothing done.\n', this_indent)

    for host in day.datapoints.keys():
        iprint('on %s' % host, base_indent)
        boot_time = datetime.datetime.fromtimestamp(day.datapoints[host][0].time) - datetime.timedelta(
            seconds=day.datapoints[host][0].uptime)
        iprint(colorize('bold', '[boot] %s\n' % boot_time.strftime(time_format)), base_indent)
        for point in day.datapoints[host]:
            if tags:
                tag_found = False
                # print(point.__dict__.keys())
                for tag in point.__dict__.get('tags', []):
                    iprint(tag, this_indent)
                    if tag in tags:
                        tag_found = True
                if tag_found:
                    print_datapoint(point, this_indent)
            else:
                print_datapoint(point, this_indent)
        if day.day.date() == datetime.datetime.today().date():
            iprint(colorize('bold', '\nup for %s now.' % humanize.naturaldelta(get_uptime())), this_indent)


def print_days(days, tags, base_indent=''):
    from doing.models import Day
    from doing.helpers import get_last_days

    if tags:
        iprint('(only tasks with %s)' % tags, base_indent)

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
            iprint("unknown argument %s. --days takes 'month' or a number of days. " % days, base_indent)

    for day in days_to_print:
        print_day(day, tags, base_indent)


def print_finish_message(fin_dict):
    if fin_dict['status'] == 'not_found':
        print('no task found!')
        return
    elif fin_dict['status'] == 'finished_before':
        fin_time = datetime.datetime.fromtimestamp(fin_dict['datapoint'].finished['time'])
        print_datapoint(fin_dict['datapoint'])
        print(colorize(['bold', 'warning'], 'task was finished @%s on %s' % (
            fin_time.strftime(time_format), fin_dict['datapoint'].finished['host'])))
        return
    else:
        fin_time = datetime.datetime.fromtimestamp(fin_dict['datapoint'].finished['time'])
        start_time = datetime.datetime.fromtimestamp(fin_dict['datapoint'].time)
        print('task "%s" \nfinished @%s (took %s)' % (
            fin_dict['datapoint'].task,
            fin_time.strftime(time_format),
            humanize.naturaldelta(fin_time - start_time)
        ))


def cmd_finish(args):
    from doing.models import Day
    from doing import time_format, hostname
    import datetime

    if touch():
        print('merged messages')
        if folder_is_git_tracked():
            git(['add', '-A'])
            git(['commit', '-m', '"%s"' % ('autocommit after touch')])

    if args == 'last':
        d = Day('today')
        try:
            if d.datapoints[hostname]:
                last_point = d.datapoints[hostname][-1]
                fin = d.finish_task(last_point.time)
                print_finish_message(fin)
            else:
                print('sorry, no last task to finish for today.')
        except Exception as e:
            logging.error('could not finish last task.', e)

    elif args == 'all':
        # finishes todays task
        d = Day('today')
        d.finish_all()

    else:
        from dateutil import parser
        try:
            parsed_date = parser.parse(args)
        except ValueError as e:
            print(colorize('warning', 'could not parse your date: %s (%s)' % (args, e)))
            return
        d = Day(parsed_date)
        if d.datapoints == {}:
            print("you have got no tasks for %s" % parsed_date.strftime(date_format + time_format))
            return
        # print(d)

        fin = d.finish_task(parsed_date.timestamp())
        print_finish_message(fin)
        # todo git commit


def cmd_touch():
    status = touch()

    if status:
        print('merged messages')
        if folder_is_git_tracked():
            git(['add', '-A'])
            git(['commit', '-m', '"%s"' % ('autocommit')])
    elif status is None:
        print('nothing to touch')
    else:
        print('something went wrong while merging messages!')
    pass


def add_task(task, finish=False):
    from doing.models import Day
    from doing.git import folder_is_git_tracked

    if touch():
        print('merged messages')
        if folder_is_git_tracked():
            git(['add', '-A'])
            git(['commit', '-m', '"%s"' % ('autocommit after touch')])

    day = Day('today')
    day.add_task(task)
    print('added')
    print_datapoint(day.datapoints[hostname][-1])
    if finish:
        fin = day.finish_task(day.datapoints[hostname][-1].time)
        print_finish_message(fin)

    if folder_is_git_tracked():
        git(['add', '-A'])
        git(['commit', '-m', '"%s - %s"' % ('autocommit', task)])
