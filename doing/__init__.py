from os.path import expanduser
import socket
import os

store_path = expanduser("~/.doing")
message_folder = os.path.join(store_path, 'messages')

hostname = socket.gethostname()

date_format = '%Y-%m-%d'
time_format = '%H:%M'

if not os.path.isdir(store_path):
    from doing.helpers import init
    print("initializing new store in %s" % store_path)
    init()
