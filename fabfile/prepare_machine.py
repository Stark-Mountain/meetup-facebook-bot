import os.path
from getpass import getpass
from io import StringIO

from fabric.api import *
from fabric.contrib.console import confirm


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def get_sources(repository_url, code_directory):
    with settings(warn_only=True):
        source_existence_check = run('test -d %s' % code_directory)
    if source_existence_check.succeeded:
        if not confirm('Code directory already exists. Remove it?'):
            print('Skipping git clone.')
            return
        sudo('rm -rf %s' % code_directory)
    sudo('git clone %s %s' % (repository_url, code_directory))


def setup_venv(code_directory):
    venv_folder = 'venv'
    with cd(code_directory):
        sudo('python3 -m venv %s' % venv_folder)
    return os.path.join(code_directory, venv_folder, 'bin')


def install_modules(code_directory, venv_bin_directory):
    requirements_path = os.path.join(code_directory, 'requirements.txt')
    venv_activate_path = os.path.join(venv_bin_directory, 'activate')
    with prefix('source %s' % venv_activate_path):
        sudo('pip install wheel')
        sudo('pip install -r %s' % requirements_path)


@task
def prepare_machine():
    install_python()
    repository_url = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'
    code_directory = '/var/www/meetup-facebook-bot'
    get_sources(repository_url, code_directory)
    venv_bin_directory = setup_venv(code_directory)
    install_modules(code_directory, venv_bin_directory)
