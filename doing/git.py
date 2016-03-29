import subprocess
from . import store_path


def folder_is_git_tracked():
    import os
    if os.path.isdir(os.path.join(store_path, '.git')):
        return True
    return False


def check_if_git():
    """
    checks if there is a git command

    :return: path to git
    """
    import shutil
    return shutil.which('git')


def git(args):
    import os
    if folder_is_git_tracked():
        git_path = check_if_git()
        if not git_path:
            print('cant find git on your system')
            return

        subprocess.call(['git'] + args, cwd=store_path)
