import argparse
import logging
import os
import json
from datetime import date, datetime
import time
from datetime import timedelta
from os.path import expanduser
import socket
import subprocess

logging.basicConfig(level=logging.DEBUG)

store_path = expanduser("~/.doing")
hostname = socket.gethostname()


def check_if_git():
    import shutil
    return shutil.which('git')

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        # td = timedelta(seconds = uptime_seconds).total_seconds()
    return uptime_seconds


def humanize_uptime(time_in_seconds):
    m, s = divmod(time_in_seconds, 60)
    h, m = divmod(m, 60)
    return '%02d:%02d' % (h, m)


def colorize(color, text):
    bcolors = {
        "HEADER": '\033[95m',
        "OKBLUE": '\033[94m',
        "OKGREEN": '\033[92m',
        "WARNING": '\033[93m',
        "FAIL": '\033[91m',
        "ENDC": '\033[0m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m'
    }
    if color.upper() in bcolors.keys():
        return '%s%s%s' % (bcolors[color.upper()], text, bcolors["ENDC"])
    else:
        return text


def get_todays_path():
    this_month = date.today().strftime('%Y%m')
    day = date.today().strftime('%d')
    if not os.path.isdir(os.path.join(store_path, this_month)):
        os.makedirs(os.path.join(store_path, this_month))
    return os.path.join(store_path, this_month, '%s_%s.json' % (day, hostname))


def load_todays_python():
    json_path = get_todays_path()
    try:
        with open(json_path, 'r') as f:
            j = json.load(f)
    except IOError as e:
        j = []
    except ValueError as e:
        # print('a new day..!')
        j = []
    return j


def first_day_of_month():
    d = date.today()
    return date(d.year, d.month, 1)


def get_hashtags(task):
    tags = []
    for word in task.split():
        if word.startswith('#') or word.startswith('+'):
            tags.append(word)
    return tags


def add_task(task):
    j = load_todays_python()
    tags = get_hashtags(task)
    now = time.time()
    uptime = get_uptime()
    point = {'time': now, 'tags:': tags, 'task': task, 'uptime': uptime}
    j.append(point)
    print('adding datapoint..')
    print_datapoint(point)
    with open(get_todays_path(), 'w+') as f:
        json.dump(j, f, indent=2)

    if os.path.isdir(os.path.join(store_path, '.git')):
        git_path = check_if_git()
        if not git_path:
            print('looks like .doing is on git, but i cant find git on your system.')
            exit(0)
        subprocess.call(['git', 'add', '-A'], cwd=store_path)
        subprocess.call(['git', 'commit', '-m', '"%s - %s"' % ('autocommit', task)], cwd=store_path)



def print_datapoint(point):
    print(colorize('bold', datetime.fromtimestamp(point['time']).strftime('%H:%M:%S')))
    print('  ' + point['task'])
    print('  pc was up for %s\n' % humanize_uptime(point['uptime']))


def print_today():
    j = load_todays_python()
    if not j:
        print('nothing done today.')
        exit(0)
    boot_time = datetime.now() - timedelta(seconds=j[0]['uptime'])
    print(colorize('bold', '[boot] %s\n' % boot_time.strftime('%H:%M:%S')))

    for point in j:
        print_datapoint(point)

    print(colorize('bold', '\nup for %s now.' % humanize_uptime(get_uptime())))


def init():
    if not os.path.isdir(store_path):
        os.makedirs(store_path)
    else:
        print("already initialized. delete %s and start again if you want to reset." % store_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="track what youre doing. tag with + or #")
    parser.add_argument("task",
                        help="what i am doing", nargs='*')
    parser.add_argument("-i", "--install",
                        help="", action="store_true")
    parser.add_argument("-g", "--git",
                        help="calls git with the arguments you give (runs in ~/.doing)", nargs='+')

    args = parser.parse_args()

    if args.install:
        shell = os.environ["SHELL"]
        if 'fish' in shell.split('/'):
            print('to install to fish:')
            print('function doing')
            print('    python3 %s $argv' % os.path.abspath(__file__))
            print('end')
            print('funcsave doing')
            exit(0)


    if not os.path.isdir(store_path):
        print("initializing new store in %s" % store_path)
        init()

    if args.git:
        git_path = check_if_git()
        if not git_path:
            print('git not found!')
            exit(0)
        git_args = []
        for arg in args.git:
            git_args += arg.split()
        subprocess.call(['git'] + git_args, cwd=store_path)
        exit(0)


    if args.task:
        add_task(' '.join(args.task))
    else:
        print_today()
