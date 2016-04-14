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
from ..helpers import _resolve_to_id, _convert_to_code
from . import console_width


def utf8len(s):
    return len(s.encode('utf-8'))


def cmd_git(args):
    git_args = []
    for arg in args:
        git_args += arg.split()

    git(git_args)


def get_timecode(datapoint):
    return _convert_to_code(int(datapoint.created))


def print_datapoint(point, base_indent=' '):
    this_indent = base_indent + '  '
    time_as_code = get_timecode(point)
    time_str = point.time_as_dt.strftime(time_format)

    spaces_betw_time_and_id = (console_width - 1 - len(time_as_code) - len(time_str) - len(this_indent))
    if point.__dict__.get('finished', False):
        iprint(icon.right_arrowhead + ' ' + time_str + ' ' * spaces_betw_time_and_id + '[' + time_as_code + ']', '',
               formatting=['bold', 'okgreen'])
        iprint('%s %s on %s (%s)' % (
            icon.check,
            datetime.datetime.fromtimestamp(point.finished['time']).strftime(time_format),
            point.finished['host'], humanize.naturaldelta(int(point.finished['time']) - int(point.time))), base_indent,
               formatting=['bold', 'okgreen'])
    else:
        iprint(icon.right_arrowhead + ' ' + time_str + ' ' * spaces_betw_time_and_id + '[' + time_as_code + ']', '',
               formatting=['bold'])

    iprint(point.task, this_indent)

    if point.time != point.created:
        if point.created_as_dt.date() == point.time_as_dt.date():
            iprint('(created @%s)\n' % (point.created_as_dt.strftime(time_format)), this_indent)
        else:
            iprint('(created @%s)\n' % (point.created_as_dt.strftime(date_format + '-' + time_format)), this_indent)
    else:
        iprint('pc was up for %s\n' % humanize.naturaldelta(point.uptime), this_indent)


def iprint(text, ind, line_len=50, formatting=[]):
    for line in text.split('\n'):
        if line == '':
            print('')
        else:
            line_to_print = [ind]
            for word in line.split(' '):
                if len(' '.join(line_to_print)) + len(word) <= line_len:
                    line_to_print.append(word)
                else:
                    print(colorize(formatting, ' '.join(line_to_print)))
                    line_to_print = [ind]
                    line_to_print.append(word)
            print(colorize(formatting, ' '.join(line_to_print)))
            # for l in wrap(line, width=console_width):
            #    print(indent(l, ind))


def print_day(day, tags, base_indent=' '):
    # bold, underlined date
    this_indent = base_indent + '  '

    iprint(colorize('bold', colorize('underline', '%s' % (day.day.strftime(date_format + ' (%A)')))), base_indent)
    if not day.datapoints:
        iprint('nothing done.\n', this_indent)

    for host in day.datapoints.keys():
        boot_time = day.datapoints[host][0].time_as_dt - datetime.timedelta(
            seconds=day.datapoints[host][0].uptime)
        if boot_time.date() == datetime.datetime.now().date():
            iprint(colorize('bold', '[boot %s] %s' % (host, boot_time.strftime(time_format))), base_indent)
        else:
            iprint(colorize('bold', '[boot %s] %s' % (host, boot_time.strftime(date_format + ' ' + time_format))),
                   base_indent)

    for point in day.get_datapoint_list():
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
        iprint(colorize('bold', '\nup for %s now.' % humanize.naturaldelta(get_uptime())), base_indent)
    """
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
    """


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
        try:
            timestamp = _resolve_to_id(args)
            parsed_date = datetime.datetime.fromtimestamp(timestamp)
        except:
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

    if '@' in task:
        time_str = task.split('@')[1].split()[0]
        parsed_time = try_parse_time(time_str)
        if not parsed_time:
            print('can not parse %s as time or date' % time_str)
            return
        #print('creating task at time %s' % parsed_time.strftime(time_format))
        day = Day(parsed_time)
        day.add_task(task, timestamp=parsed_time.timestamp())
    else:
        day.add_task(task)

    print('added')
    print_datapoint(day.datapoints[hostname][-1])
    if finish:
        fin = day.finish_task(day.datapoints[hostname][-1].time)
        print_finish_message(fin)

    if folder_is_git_tracked():
        git(['add', '-A'])
        git(['commit', '-m', '"%s - %s"' % ('autocommit', task)])
