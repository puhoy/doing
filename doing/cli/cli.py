import logging
import humanize
import datetime
from ..helpers import get_uptime, try_parse_time
from ..cli.colorize import colorize
from .. import time_format, date_format, hostname
from ..git import git


def cmd_git(args):
    git_args = []
    for arg in args:
        git_args += arg.split()

    git(git_args)


def print_datapoint(point):
    if point.__dict__.get('finished', False):
        print(
            colorize(['bold', 'okgreen'],
                     '  ' + datetime.datetime.fromtimestamp(point.time).strftime(time_format)))

        print('  finished @%s on %s ' % (
            datetime.datetime.fromtimestamp(point.finished['time']).strftime(time_format),
            point.finished['host']))

    else:
        print(colorize('bold', '  ' + datetime.datetime.fromtimestamp(point.time).strftime(time_format)))

    print('    ' + point.task)
    print('    pc was up for %s\n' % humanize.naturaldelta(point.uptime))

    # print(point.finished)


def print_day(day, tags):
    # bold, underlined date
    print(colorize('bold', colorize('underline', '%s' % (day.day.strftime(date_format + ' (%A)')))))
    if not day.datapoints:
        print('nothing done.\n')

    for host in day.datapoints.keys():
        print('on %s' % host)
        boot_time = datetime.datetime.fromtimestamp(day.datapoints[host][0].time) - datetime.timedelta(
            seconds=day.datapoints[host][0].uptime)
        print(colorize('bold', '[boot] %s\n' % boot_time.strftime(time_format)))
        for point in day.datapoints[host]:
            if tags:
                tag_found = False
                # print(point.__dict__.keys())
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
            print("unknown argument %s. --days takes 'month' or a number of days. " % days)

    for day in days_to_print:
        print_day(day, tags)


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
        parsed_date = parser.parse(args)
        d = Day(parsed_date)
        if d.datapoints == {}:
            print("you have got no tasks for %s" % parsed_date.date())
            return
        # print(d)

        fin = d.finish_task(parsed_date.timestamp())
        print_finish_message(fin)
        # todo git commit


def cmd_touch():
    from doing.git import folder_is_git_tracked
    from doing.helpers import touch
    if touch():
        print('merged messages')
        if folder_is_git_tracked():
            git(['add', '-A'])
            git(['commit', '-m', '"%s"' % ('autocommit')])
    else:
        print('nothing to touch')
    pass


def add_task(task, finish=False):
    from doing.models import Day
    from doing.git import folder_is_git_tracked
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

    pass
