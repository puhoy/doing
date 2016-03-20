
def get_last_days(number_of_days):
    """

    :param number_of_days:
    :return: returns an array of days
    """
    from doing.models import Day
    from datetime import datetime, timedelta
    days = []
    for i in reversed(range(0, number_of_days)):
        d = datetime.now() - timedelta(days=i)
        days.append(Day(d))
    return days


def init():
    """
    initialize the store folder at ~/.doing
    complains if folder is already there.

    :return:
    """
    import os
    import logging
    from . import store_path

    if not os.path.isdir(store_path):
        os.makedirs(store_path)
    else:
        logging.error("already initialized. delete %s and start again if you want to reset." % store_path)


def colorize(color, text):
    """
    colorize terminal output

    :param color: [header, okblue, okgreen, ...]
    :param text: text to colorize
    :return: colorized text, ready to print
    """
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

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        # td = timedelta(seconds = uptime_seconds).total_seconds()
    return uptime_seconds