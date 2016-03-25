import datetime
import humanize
import os
import json
import fnmatch
import logging
import time
from dateutil import parser
from . import store_path, hostname as this_hostname, message_folder


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
        self._load_datapoints()
        self.process_messages()

    def get_datapoint_list(self):
        all_points = []
        for host in self.datapoints:
            all_points += self.datapoints[host]
        return sorted(all_points, key=lambda k: k.time)

    def _load_datapoints(self):
        self.datapoints = {}
        logging.debug('loading from %s' % self.path_for_this_host)
        if os.path.isdir(self.path_for_this_days_folder):
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
            logging.debug('loaded regular datapoints')


    def add_task(self, task, hostname=this_hostname):
        if not self.datapoints.get(hostname, False):
            self.datapoints[hostname] = []
        self.datapoints[hostname].append(Datapoint(task=task))
        self.write()

    def get_datapoint_by_timestamp(self, timestamp, hostname=None):
        """
        iterate over all datapoints until we found

        :param timestamp:
        :return: a dict with keys "hostname" and "datapoint"
        """
        hosts = []
        if not hostname:
            for host in self.datapoints:
                hosts.append(host)
        else:
            hosts.append(hostname)

        for host in hosts:
            logging.debug('searching in points for %s' % hosts)
            #logging.debug(self.datapoints)
            for point in self.datapoints[host]:
                if int(timestamp) == int(point.time):
                    return {'hostname': host,
                            'datapoint': point }

    def write(self, hostname=this_hostname):
        points_to_write = []
        if not self.datapoints.get(hostname, False):
            self.datapoints[hostname] = []
        for point in self.datapoints[hostname]:
            points_to_write.append(point.__dict__)
        if not os.path.isdir(self.path_for_this_days_folder):
            os.mkdir(self.path_for_this_days_folder)
        with open(self.path_for_this_host, 'w+') as f:
            json.dump(points_to_write, f, indent=2)

    def finish_all(self):
        for host in self.datapoints:
            for point in host:
                if host == this_hostname:
                    point.finish()
                else:
                    self.craft_finish_message(point)

    def finish_task(self, timestamp, host=None):
        """


        :param timestamp:
        :param host:
        :return:
            False, if no point was found
            True, if finished
            returns timestamp-and-host dict, if task was finished before
        """
        d = self.get_datapoint_by_timestamp(timestamp)
        if not d:
            logging.debug('no point for timestamp found')
            return {'status': 'not_found'}
        logging.debug('found datapoint %s' % d)
        hostname = d['hostname']
        dp = d['datapoint']
        if dp.__dict__.get('finished', False):
            logging.debug('was finished before')
            return {'status': 'finished_before',
                    'datapoint': dp }

        if hostname == this_hostname:
            logging.debug('yup, found. finishing.')
            dp.finish()
            self.write()
        else:
            logging.debug('found on another host, writing a message...')
            self.craft_finish_message(dp, hostname)
            pass
        return {'status': 'ok',
                'datapoint': dp }

    def process_messages(self):
        """
        merges massages to datapoints

        to merge messages for this host permanently, see helpers.process_messages
        :return:
        """
        for f in os.listdir(message_folder):
            if fnmatch.fnmatch(
                os.path.join(message_folder, f),
                    os.path.join(message_folder, 'dear_*_*.json')):
                date_in_filename = f.split('_')[3].split(".json")[0]
                parser.parse(date_in_filename).date()
                if self.day.date() == parser.parse(date_in_filename).date():

                    logging.debug('found a message %s' % f)
                    with open(os.path.join(message_folder, f)) as message_file:
                        message = json.load(message_file)
                    self.merge_message_to_datapoint(message)

    def _sort_by_time(self):
        # todo
        pass

    def merge_message_to_datapoint(self, message):
        """
        merge a (finish-) message in our tasks

        :param message: message to merge
        :param write: write new datapoints to disk
        :param dest_host: host who gets the message
        :return:
        """
        if message['subject'] == 'finished':
            dest_hostname = message['to']
            source_hostname = message['from']
            timestamp = message['datapoint']['time']

            found_dp = self.get_datapoint_by_timestamp(timestamp, hostname=dest_hostname)
            if not found_dp:
                logging.error('cant find destination task for %s' % message)
                return False
            found_dp['datapoint'].finish(timestamp=message['time'], hostname=source_hostname)
            return True
        else:
            logging.error('got a strange message %s' % message)
            return False


    def craft_finish_message(self, datapoint, destination_host):
        """
        used to finish tasks on other hosts
        (basically leaves them a message)

        :return:
        """
        message_path = os.path.join(
                message_folder,
                'dear_%s_0_%s.json' % (destination_host, datetime.datetime.fromtimestamp(datapoint.time).strftime('%Y%m%d-%H:%M:%S'))
            )

        # if the name is already given, iterate a bit
        i = 0
        while os.path.isfile(message_path):
            i += 1
            message_path = os.path.join(
                message_folder,
                'dear_%s_%s_%s.json' % (destination_host, i, datetime.datetime.fromtimestamp(datapoint.time).strftime('%Y%m%d-%H:%M:%S'))
            )

        message = {
            'time': time.time(),
            'from': this_hostname,
            'to': destination_host,
            'subject': 'finished',
            'datapoint': datapoint.__dict__
        }
        with open(message_path, 'w+') as f:
            json.dump(message, f, indent=2)
        self.process_messages()
        return True



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

    def finish(self, timestamp=datetime.datetime.now().timestamp(), hostname=this_hostname):
        """
        call this ONLY if you are on the host that created this point,
        or maybe possibly eventually you will run into git merges.
        In that case you should use Day('').finish_task()

        :param timestamp:
        :param hostname: host on which this task was finished
        :return:
        """
        self.finished = {
            'time': timestamp,
            'host': hostname
        }
        self.update(timestamp)

    def update(self, timestamp=datetime.datetime.now().timestamp()):
        self.updated = timestamp
