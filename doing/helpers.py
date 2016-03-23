def process_messages():
    """
    looks for messages for this host & merges to the tasks

    :return: true is a message was found, else false
    """
    import logging
    import os
    from . import message_folder, hostname
    from .models import Day
    import json
    from dateutil import parser
    import time
    from datetime import datetime
    import fnmatch

    logging.debug('processing messages')
    for f in os.listdir(message_folder):
        date_in_filename = f.split('_')[3].split(".json")[0]
        logging.debug('date in filename %s' % date_in_filename)
        # if day.date() == parser.parse(date_in_filename).date():
        # if the message is for us
        found = None
        error = False
        if fnmatch.fnmatch(
                os.path.join(message_folder, f),
                os.path.join(message_folder, 'dear_%s_*.json' % hostname)):
            logging.debug('found a message for us: %s' % f)
            with open(os.path.join(message_folder, f)) as message_file:
                message = json.load(message_file)
                d = datetime.combine(parser.parse(date_in_filename).date(), datetime.min.time())
                day = Day(d)
                if day.merge_message_to_datapoint(message):
                    day.write()
                    found = True
                    os.remove(os.path.join(message_folder, f))
                else:
                    error = True
        if error:
            return False
        return found


def touch():
    status = process_messages()
    return status


def get_last_days(number_of_days):
    """

    :param number_of_days:
    :return: returns an array of days
    """
    from .models import Day
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
