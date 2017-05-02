from getpass import getpass
from io import StringIO

from fabric.api import settings, local, abort, run, cd, env, prefix, sudo, prompt, put
from fabric.contrib.console import confirm 

env.sources_directory = '/var/www/meetup-facebook-bot'
env.socket_path = '/tmp/meetup-facebook-bot.socket' % env.sources_directory
env.venv_folder = 'venv'
env.venv_activate_command = 'source %s/%s/bin/activate' % (env.sources_directory, env.venv_folder)
env.app_ini_filepath = '%s/meetup-facebook-bot.ini' % env.sources_directory


#TODO: add prepare_deploy task
#TODO: add deploy task
#TODO: implement the rest


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def get_sources():
    repository_url = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'  
    sudo('git clone %s %s' % (repository_url, env.sources_directory))


def setup_venv():
    with cd(env.sources_directory):
        sudo('python3 -m venv %s' % env.venv_folder)


def install_modules():
    requirements_path = '%s/requirements.txt' % env.sources_directory
    with prefix(env.venv_activate_command):
        sudo('pip install wheel')
        sudo('pip install -r %s' % requirements_path)


def prepare_sources():
    install_python()
    get_sources()
    setup_venv()
    install_modules()


def install_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')


def install_database():
    sudo('apt-get update')
    sudo('apt-get install postgresql postgresql-contrib')


def setup_database():
    db_username = env.user
    db_name = env.user
    run('sudo -u postgres createuser %s -s' % db_username)
    run('sudo -u postgres createdb %s' % db_name)
    env.database_url = 'postgresql://%s@/%s' % (db_username, db_name)

def setup_firewall():
    sudo('ufw allow "Nginx Full"')
    sudo('ufw allow OpenSSH')
    sudo('ufw enable')


def create_ini_file():
    database_url = getattr(env, 'database_url', prompt('Enter DATABASE_URL:'))
    access_token = getpass('Enter ACCESS_TOKEN:')
    page_id = prompt('Enter PAGE_ID:')
    app_id = prompt('Enter APP_ID:')
    verify_token = getpass('Enter VERIFY_TOKEN:')
    put(StringIO(
u'''[uwsgi]
env = DATABASE_URL={db_url}
env = ACCESS_TOKEN={access_token}
env = PAGE_ID={page_id}
env = APP_ID={app_id}
env = VERIFY_TOKEN={verify_token}

module = wsgi:app
master = true
processes = 4
socket = {socket_path}
chmod-socket = 660
vacuum = true
die-on-term = true'''.format(
                db_url=database_url,
                access_token=access_token,
                page_id=page_id,
                app_id=app_id,
                verify_token=verify_token,
                socket_path=env.socket_path
            )
        ), 
        env.app_ini_filepath,
        use_sudo=True
    )


def create_service_file():
    pass


def create_nginx_config():
    pass


def start_service():
    pass


def start_nginx():
    sudo('systemctl start nginx')


def run_setup_scripts():
    # setup database and get_started button
    pass


def prepare_machine():
    pass
