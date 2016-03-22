
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
    from . import store_path, message_folder

    if not os.path.isdir(store_path):
        os.makedirs(store_path)
    else:
        logging.error("already initialized. delete %s and start again if you want to reset." % store_path)
    if not os.path.isdir(message_folder):
        os.makedirs(message_folder)


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        # td = timedelta(seconds = uptime_seconds).total_seconds()
    return uptime_seconds

def try_parse_time(to_parse):
    """
    try to convert string or int or float to a datetime

    :param to_parse:
    :return: datetime
    """
    from dateutil import parser
    from datetime import datetime
    # dateutil does not parse unix timestamps
    try:
        d = datetime.fromtimestamp(float(to_parse))
        return d
    except:
        try:
            d = parser.parse(to_parse)
            return d
        except:
            return False





