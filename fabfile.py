import os.path
from getpass import getpass
from collections import OrderedDict

from fabric.api import sudo, run, cd, prefix, settings, task, env, prompt, shell_env,\
        local, abort
from fabric.contrib.console import confirm
from fabric.contrib.files import exists, upload_template

env.hosts = ['vergeev@meetup-bot.me']

PROJECT_FOLDER = '/var/www/meetup-facebook-bot'  # must not end with '/'
PERMANENT_PROJECT_FOLDER = "%s.permanent" % PROJECT_FOLDER
REPOSITORY_URL = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'
UWSGI_SERVICE_NAME = 'meetup-facebook-bot.service'
SOCKET_PATH = '/tmp/meetup-facebook-bot.socket'
INI_FILE_PATH = os.path.join(PERMANENT_PROJECT_FOLDER, 'meetup-facebook-bot.ini')
VENV_FOLDER = 'venv'
VENV_BIN_DIRECTORY = os.path.join(PERMANENT_PROJECT_FOLDER, VENV_FOLDER, 'bin')
DHPARAM_PATH = '/etc/ssl/certs/dhparam.pem'
SSL_PARAMS_PATH = '/etc/nginx/snippets/ssl-params.conf'


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def fetch_sources_from_repo(repository_url, branch, code_directory):
    if exists(code_directory):
        print('Removing the following directory: %s' % code_directory)
        sudo('rm -rf %s' % code_directory)
    git_clone_command = 'git clone {1} {2} --branch {0} --single-branch'
    sudo(git_clone_command.format(branch, repository_url, code_directory))


def reinstall_venv():
    with cd(PERMANENT_PROJECT_FOLDER):
        sudo('rm -rf %s' % VENV_FOLDER)
        sudo('python3 -m venv %s' % VENV_FOLDER)


def install_modules(code_directory, venv_bin_directory):
    requirements_path = os.path.join(code_directory, 'requirements.txt')
    venv_activate_path = os.path.join(venv_bin_directory, 'activate')
    with prefix('source %s' % venv_activate_path):
        sudo('pip install wheel')
        sudo('pip install -r %s' % requirements_path)


def install_nginx():
    sudo('apt-get update')
    sudo('apt-get install nginx')


def install_postgres():
    sudo('apt-get update')
    sudo('apt-get install postgresql postgresql-contrib')


def setup_ufw():
    sudo('ufw allow "Nginx Full"')
    sudo('ufw allow OpenSSH')
    sudo('echo "y" | ufw enable')


def setup_postgres(username, database_name):
    with settings(warn_only=True):
        sudo('sudo -u postgres createuser %s -s' % username)
        sudo('sudo -u postgres createdb %s' % database_name)
    return 'postgresql://%s@/%s' % (username, database_name)


def start_letsencrypt_setup():
    sudo("mkdir -p /tmp/git")
    sudo("rm -rf /tmp/git/letsencrypt")
    with cd("/tmp/git"):
        sudo("git clone https://github.com/letsencrypt/letsencrypt")
    with cd("/tmp/git/letsencrypt"):
        sudo('./letsencrypt-auto certonly --standalone')
    sudo('rm -rf /tmp/git')


def start_uwsgi(uwsgi_service_name):
    sudo('systemctl daemon-reload')
    sudo('systemctl enable %s' % uwsgi_service_name)
    sudo('systemctl restart %s' % uwsgi_service_name)


def start_nginx():
    sudo('systemctl enable nginx')
    sudo('systemctl restart nginx')


def run_setup_scripts(access_token, database_url, venv_bin_directory, code_directory):
    environ_params = {
        'ACCESS_TOKEN': access_token,
        'DATABASE_URL': database_url,
    }
    venv_activate_path = os.path.join(venv_bin_directory, 'activate')
    venv_activate_command = 'source %s' % venv_activate_path
    with cd(code_directory), shell_env(**environ_params), prefix(venv_activate_command):
        run('python3 %s/database_setup.py' % code_directory)
        run('python3 %s/set_start_button.py' % code_directory)


def prompt_for_environment_variables(env_vars):
    for env_var, value in env_vars.items():
        if value is None or confirm('%s is set. Change it?'):
            env_vars[env_var] = prompt('Enter %s:' % env_var)
    return env_vars


@task
def renew_ini_file(database_url=None):
    env_vars = OrderedDict(
        [
            ('DATABASE_URL', None),
            ('PAGE_ID', None),
            ('APP_ID', None),
            ('ACCESS_TOKEN', None),
            ('VERIFY_TOKEN', None),
            ('SECRET_KEY', None),
            ('ADMIN_LOGIN', None),
            ('ADMIN_PASSWORD', None),
        ]
    )
    env_vars['DATABASE_URL'] = database_url
    env_vars = prompt_for_environment_variables(env_vars)
    config_vars = env_vars.copy()
    config_vars['SOCKET_PATH'] = SOCKET_PATH
    upload_template(
        filename='deploy_configs/meetup-facebook-bot.ini',
        destination=INI_FILE_PATH,
        context=config_vars,
        use_sudo=True
    )
    env.env_vars = env_vars


def create_permanent_folder():
    with settings(warn_only=True):
        sudo('mkdir %s' % PERMANENT_PROJECT_FOLDER)


def create_service_file():
    service_file_config = {
        'user': env.user,
        'work_dir': PROJECT_FOLDER,
        'env_bin_dir': VENV_BIN_DIRECTORY,
        'uwsgi_path': os.path.join(VENV_BIN_DIRECTORY, 'uwsgi'),
        'app_ini_path': INI_FILE_PATH
    }
    upload_template(
        filename='deploy_configs/meetup-facebook-bot.service',
        destination=os.path.join('/etc/systemd/system/', UWSGI_SERVICE_NAME),
        context=service_file_config,
        use_sudo=True
    )


def create_dhparam_if_necessary():
    if exists(DHPARAM_PATH):
        print('dhparam file exists, skipping this step')
        return
    sudo('openssl dhparam -out %s 2048' % DHPARAM_PATH)


def create_ssl_params_if_necessary():
    create_dhparam_if_necessary()
    if exists(SSL_PARAMS_PATH):
        print('Not creating ssl-params.conf, already exists')
        return
    upload_template(
        filename='deploy_configs/ssl_params',
        destination=SSL_PARAMS_PATH,
        context={'dhparam_path': DHPARAM_PATH},
        use_sudo=True
    )


def configure_letsencrypt_if_necessary():
    create_ssl_params_if_necessary()
    env.letsencrypt_folder = os.path.join('/etc/letsencrypt/live', env.domain_name)
    print('Assuming letsencrypt folder is %s' % env.letsencrypt_folder)
    if exists(env.letsencrypt_folder):
        print('letsencrypt folder found, skipping letsencrypt setup')
        return
    start_letsencrypt_setup()


@task
def bootstrap(branch='master'):
    env.sudo_password = getpass('Initial value for env.sudo_password: ')
    env.domain_name = prompt('Enter your domain name:', default='meetup_facebook_bot')

    create_permanent_folder()
    install_postgres()
    database_url = setup_postgres(username=env.user, database_name=env.user)
    renew_ini_file(database_url)

    install_python()
    fetch_sources_from_repo(REPOSITORY_URL, branch=branch, code_directory=PROJECT_FOLDER)
    reinstall_venv()
    install_modules(PROJECT_FOLDER, VENV_BIN_DIRECTORY)
    install_nginx()
    setup_ufw()

    configure_letsencrypt_if_necessary()

    nginx_config_path = os.path.join('/etc/nginx/sites-available', env.domain_name)
    nginx_installed = exists(nginx_config_path)

    if nginx_installed:
        print('nginx config found, won\'t add restart job to crontab')
    else:
        # needed for successful ssl certificate renewal
        sudo('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')

    if nginx_installed:
        print('nginx config found, not creating another one')
    else:
        nginx_config_variables = {
            'source_dir': PROJECT_FOLDER,
            'domain': env.domain_name,
            'ssl_params_path': SSL_PARAMS_PATH,
            'fullchain_path': os.path.join(env.letsencrypt_folder, 'fullchain.pem'),
            'privkey_path': os.path.join(env.letsencrypt_folder, 'privkey.pem'),
            'socket_path': SOCKET_PATH
        }
        upload_template(
            filename='deploy_configs/nginx_config',
            destination=nginx_config_path,
            context=nginx_config_variables,
            use_sudo=True
        )
    nginx_config_alias = os.path.join('/etc/nginx/sites-enabled', env.domain_name)
    sudo('ln -sf %s %s' % (nginx_config_path, nginx_config_alias))

    start_uwsgi(UWSGI_SERVICE_NAME)
    start_nginx()
    access_token = env.env_vars['ACCESS_TOKEN']
    database_url = env.env_vars['DATABASE_URL']
    run_setup_scripts(access_token, database_url, VENV_BIN_DIRECTORY, PROJECT_FOLDER)


@task
def deploy(branch='master'):
    update_dependencies = confirm('Update dependencies?')
    print('OK, deploying branch %s' % branch)
    env.sudo_password = getpass('Initial value for env.sudo_password: ')
    fetch_sources_from_repo(REPOSITORY_URL, branch, PROJECT_FOLDER)
    if update_dependencies:
        venv_bin_path = reinstall_venv(PERMANENT_PROJECT_FOLDER)
        install_modules(PROJECT_FOLDER, venv_bin_path)
    start_uwsgi(UWSGI_SERVICE_NAME)
    start_nginx()


def print_service_status(service_name):
    sudo('systemctl status %s' % service_name)


@task
def status():
    env.sudo_password = getpass('Initial value for env.sudo_password: ')
    print_service_status(UWSGI_SERVICE_NAME)


def test():
    with settings(warn_only=True):
        result = local('python3 -m pytest tests', capture=True)
    if result.failed and not confirm('Tests failed. Continue anyway?'):
        abort('Aborting at user request.')


def git_commit():
    with settings(warn_only=True):
        local('git add -i && git commit')


def push(branch):
    local('git push origin %s' % branch)


@task
def commit(branch):
    test()
    git_commit()
    push(branch)
