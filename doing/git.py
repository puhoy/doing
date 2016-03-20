import subprocess
from . import store_path


def check_if_git():
    """
    checks if there is a git command

    :return: path to git
    """
    import shutil
    return shutil.which('git')


def git(args):
    subprocess.call(['git'] + args, cwd=store_path)