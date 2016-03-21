import datetime
import humanize
import os
import json
import fnmatch
import logging
import time

from . import store_path, hostname as this_hostname


def load_or_create_dict(path):
    logging.debug('loading %s', path)
    json_path = path
    try:
        with open(json_path, 'r') as f:
            j = json.load(f)
    except IOError as e:
        j = []
    except ValueError as e:
        j = []
    return j


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        # td = timedelta(seconds = uptime_seconds).total_seconds()
    return uptime_seconds


def get_hashtags(task):
    tags = []
    for word in task.split():
        if word.startswith('#') or word.startswith('+'):
            tags.append(word)
    return tags




class Day:
    def __init__(self, day, hostname=''):
        """
        represents a day

        :param day: may be a datetime, a date string, 'today' or 'yesterday'
        :return:
        """

        if isinstance(day, datetime.datetime):
            self.day = day

        elif day in ['today']:
            self.day = datetime.datetime.today()

        elif day in ['yesterday']:
            self.day = datetime.datetime.today() - datetime.timedelta(days=1)

        self.hostname = hostname

        self.path_for_this_days_folder = os.path.join(
            store_path,
            self.day.strftime('%Y%m'))

        self.path_for_this_host = os.path.join(
            store_path,
            self.day.strftime('%Y%m'),
            self.day.strftime('%d') + '_%s.json' % this_hostname)

        if self.hostname:
            # if hostname is given, we restrict the wildcard
            self.path_wildcard = os.path.join(
                store_path,
                self.day.strftime('%Y%m'),
                self.day.strftime('%d') + '_%s.json' % hostname)
        else:
            self.path_wildcard = os.path.join(
                store_path,
                self.day.strftime('%Y%m'),
                self.day.strftime('%d') + '_*.json')

        self.datapoints = {}
        logging.debug('loading from %s' % self.path_for_this_host)
        for f in os.listdir(self.path_for_this_days_folder):
            if fnmatch.fnmatch(
                    os.path.join(self.path_for_this_days_folder, f),
                    self.path_wildcard):
                hostname = f.split('_')[1].split('.')[0]
                points = load_or_create_dict(os.path.join(self.path_for_this_days_folder, f))
                for point in points:
                    if not self.datapoints.get(hostname, False):
                        self.datapoints[hostname] = []
                    self.datapoints[hostname].append(Datapoint(dp_dict=point))

    def add_task(self, task, hostname=this_hostname):
        if not self.datapoints.get(hostname, False):
            self.datapoints[hostname] = []
        self.datapoints[hostname].append(Datapoint(task=task))
        self.write()

    def get_datapoint_by_timestamp(self, timestamp):
        pass

    def get_datapoint_by_time(self, time):
        pass

    def get_datapoint_by_date(self, date_str):
        pass

    def write(self, hostname=this_hostname):
        points_to_write = []
        if not self.datapoints.get(hostname, False):
            self.datapoints[hostname] = []
        for point in self.datapoints[hostname]:
            points_to_write.append(point.__dict__)
        with open(self.path_wildcard, 'w+') as f:
            json.dump(points_to_write, f, indent=2)


class Datapoint():
    def __init__(self, dp_dict=None, task=''):
        if dp_dict is None:
            dp_dict = {
                'time': time.time(),
                'tags': get_hashtags(task),
                'task': task,
                'uptime': get_uptime()
            }
        self.__dict__.update(dp_dict)

    def __repr__(self):
        return '<%s>' % str(self.__dict__)

    def finish(self, timestamp=datetime.datetime.now().timestamp()):
        self.finished = timestamp
        self.update(timestamp)

    def update(self, timestamp=datetime.datetime.now().timestamp()):
        self.updated = timestamp
