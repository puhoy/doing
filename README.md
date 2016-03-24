## doing

track what you are doing
with git installed, you can track tasks over multiple hosts.
   
    positional arguments:
      task                  what i am doing
       
    optional arguments:
      -h, --help            show this help message and exit
      -f [FINISH], --finish [FINISH]
                            set task as finished. defaults to the 'last' task, may
                            be time or date of task 'all' finishes all of today'
      --git GIT [GIT ...]   calls git with the arguments you give (runs in
                            ~/.doing)
      --days DAYS           prints a number of days or this 'month'.
      --tags TAGS [TAGS ...]
                            restrict prints to tasks with tags
      --touch               try to merge messages for this host, trigger a git
                            commit
    

returns a log of your day when called without arguments.


### setup

    python3 setup.py install
    
    # or
    
    sudo python3 setup.py install
  

