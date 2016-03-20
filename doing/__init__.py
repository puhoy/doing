from os.path import expanduser
import socket
import os

store_path = expanduser("~/.doing")
hostname = socket.gethostname()

date_format = '%Y-%m-%d'
time_format = '%H:%M:%S'




if not os.path.isdir(store_path):
    print("initializing new store in %s" % store_path)
    init()
