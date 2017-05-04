import os.path
from getpass import getpass
from io import BytesIO

from fabric.api import sudo, run, cd, prefix, settings, task, env, put, prompt
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


def install_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')
    run('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')


def install_postgres():
    sudo('apt-get update')
    sudo('apt-get install postgresql postgresql-contrib')


def setup_ufw():
    sudo('ufw allow "Nginx Full"')
    sudo('ufw allow OpenSSH')
    sudo('ufw enable')


def setup_postgres(username, database_name):
    with settings(warn_only=True):
        run('sudo -u postgres createuser %s -s' % username)
        run('sudo -u postgres createdb %s' % database_name)
    return 'postgresql://%s@/%s' % (username, database_name)


def load_text_from_file(filepath):
    with open(filepath) as text_file:
        return text_file.read()


def create_ini_file(ini_file_template, ini_file_path, **kwargs):
    ini_file = ini_file_template.format(**kwargs)
    put(BytesIO(ini_file.encode('utf-8')), ini_file_path, use_sudo=True)


@task
def prepare_machine():
    install_python()
    repository_url = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'
    code_directory = '/var/www/meetup-facebook-bot'
    get_sources(repository_url, code_directory)
    venv_bin_directory = setup_venv(code_directory)
    install_modules(code_directory, venv_bin_directory)
    install_nginx()
    install_postgres()
    setup_ufw()
    database_url = setup_postgres(username=env.user, database_name=env.user)
    access_token = getpass('Enter the app ACCESS_TOKEN: ')
    socket_path = '/tmp/meetup-facebook-bot.socket'
    ini_file_path = os.path.join(code_directory, 'meetup-facebook-bot.ini')
    create_ini_file(
        ini_file_template=load_text_from_file('fabfile/templates/meetup-facebook-bot.ini'),
        ini_file_path=ini_file_path,
        database_url=database_url,
        access_token=access_token,
        page_id=prompt('Enter PAGE_ID:'),
        app_id=prompt('Enter APP_ID:'),
        verify_token=getpass('Enter VERIFY_TOKEN: '),
        socket_path=socket_path
    )
