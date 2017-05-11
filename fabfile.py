import os.path
from getpass import getpass
from io import BytesIO

from fabric.api import sudo, run, cd, prefix, settings, task, env, put, prompt, shell_env,\
        local, abort
from fabric.contrib.console import confirm

env.hosts = ['vergeev@meetup-bot.me']

PROJECT_FOLDER = '/var/www/meetup-facebook-bot'  # must not end with '/'
PERMANENT_PROJECT_FOLDER = "%s.permanent" % PROJECT_FOLDER
REPOSITORY_URL = 'https://github.com/Stark-Mountain/meetup-facebook-bot.git'
UWSGI_SERVICE_NAME = 'meetup-facebook-bot.service'


def exists_on_remote(path):
    with settings(warn_only=True):
        existence_check = run('test -e %s' % path)
    return existence_check.succeeded


def install_python():
    sudo('apt-get update')
    sudo('apt-get install python3-pip python3-dev python3-venv')


def fetch_sources_from_repo(repository_url, branch, code_directory):
    if exists_on_remote(code_directory):
        print('Removing the following directory: %s' % code_directory)
        sudo('rm -rf %s' % code_directory)
    git_clone_command = 'git clone {1} {2} --branch {0} --single-branch'
    sudo(git_clone_command.format(branch, repository_url, code_directory))


def reinstall_venv(venv_directory):
    venv_folder = 'venv'
    with cd(venv_directory):
        sudo('rm -rf %s' % venv_folder)
        sudo('python3 -m venv %s' % venv_folder)
    return os.path.join(venv_directory, venv_folder, 'bin')


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


def load_text_from_file(filepath):
    with open(filepath) as text_file:
        return text_file.read()


def put_formatted_template_on_server(template, destination_file_path, **kwargs):
    formatted_template = template.format(**kwargs)
    put(BytesIO(formatted_template.encode('utf-8')), destination_file_path, use_sudo=True)


def create_dhparam_if_necessary(dhparam_path):
    if exists_on_remote(dhparam_path):
        print('dhparam file exists, skipping this step')
        return
    sudo('openssl dhparam -out %s 2048' % dhparam_path)


def configure_letsencrypt():
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


@task
def prepare_machine(branch='master'):
    env.sudo_password = getpass('Initial value for env.sudo_password: ')
    domain_name = prompt('Enter your domain name:', default='meetup_facebook_bot')
    page_id = prompt('Enter PAGE_ID:')
    app_id = prompt('Enter APP_ID:')
    access_token = getpass('Enter the app ACCESS_TOKEN: ')
    verify_token = getpass('Enter VERIFY_TOKEN: ')
    secret_key = getpass('Enter SECRET_KEY: '),
    admin_login = getpass('Enter ADMIN_LOGIN: ')
    admin_password = getpass('Enter ADMIN_PASSWORD: ')

    with settings(warn_only=True):
        sudo('mkdir %s' % PERMANENT_PROJECT_FOLDER)

    install_python()
    fetch_sources_from_repo(REPOSITORY_URL, branch=branch, code_directory=PROJECT_FOLDER)
    venv_bin_directory = reinstall_venv(PERMANENT_PROJECT_FOLDER)
    install_modules(PROJECT_FOLDER, venv_bin_directory)
    install_nginx()
    install_postgres()
    setup_ufw()

    database_url = setup_postgres(username=env.user, database_name=env.user)
    socket_path = '/tmp/meetup-facebook-bot.socket'
    ini_file_path = os.path.join(PERMANENT_PROJECT_FOLDER, 'meetup-facebook-bot.ini')
    put_formatted_template_on_server(
        template=load_text_from_file('deploy_configs/meetup-facebook-bot.ini'),
        destination_file_path=ini_file_path,
        database_url=database_url,
        access_token=access_token,
        page_id=page_id,
        app_id=app_id,
        verify_token=verify_token,
        socket_path=socket_path,
        secret_key=secret_key,
        admin_login=admin_login,
        admin_password=admin_password
    )

    put_formatted_template_on_server(
        template=load_text_from_file('deploy_configs/meetup-facebook-bot.service'),
        destination_file_path=os.path.join('/etc/systemd/system/', UWSGI_SERVICE_NAME),
        user=env.user,
        work_dir=PROJECT_FOLDER,
        env_bin_dir=venv_bin_directory,
        uwsgi_path=os.path.join(venv_bin_directory, 'uwsgi'),
        app_ini_path=ini_file_path
    )

    dhparam_path = '/etc/ssl/certs/dhparam.pem'
    create_dhparam_if_necessary(dhparam_path)
    ssl_params_path = '/etc/nginx/snippets/ssl-params.conf'
    if exists_on_remote(ssl_params_path):
        print('Not creating ssl-params.conf, already exists')
    else:
        put_formatted_template_on_server(
            template=load_text_from_file('deploy_configs/ssl_params'),
            destination_file_path=ssl_params_path,
            dhparam_path=dhparam_path
        )

    nginx_config_path = os.path.join('/etc/nginx/sites-available', domain_name)
    nginx_installed = exists_on_remote(nginx_config_path)
    if nginx_installed:
        print('nginx config found, skipping letsencrypt setup')
    else:
        configure_letsencrypt()
        letsnecrypt_folder = os.path.join('/etc/letsencrypt/live', domain_name)
        print('Assuming letsencrypt folder is %s' % letsnecrypt_folder)

    if nginx_installed:
        print('nginx config found, won\'t add restart job to crontab')
    else:
        # needed for successful ssl certificate renewal
        sudo('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')

    if nginx_installed:
        print('nginx config found, not creating another one')
    else:
        put_formatted_template_on_server(
            template=load_text_from_file('deploy_configs/nginx_config'),
            destination_file_path=nginx_config_path,
            source_dir=PROJECT_FOLDER,
            domain=domain_name,
            ssl_params_path=ssl_params_path,
            fullchain_path=os.path.join(letsnecrypt_folder, 'fullchain.pem'),
            privkey_path=os.path.join(letsnecrypt_folder, 'privkey.pem'),
            socket_path=socket_path
        )
    nginx_config_alias = os.path.join('/etc/nginx/sites-enabled', domain_name)
    sudo('ln -sf %s %s' % (nginx_config_path, nginx_config_alias))

    start_uwsgi(UWSGI_SERVICE_NAME)
    start_nginx()
    run_setup_scripts(access_token, database_url, venv_bin_directory, PROJECT_FOLDER)


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
def show_status():
    env.sudo_password = getpass('Initial value for env.sudo_password: ')
    print_service_status(UWSGI_SERVICE_NAME)


def test():
    with settings(warn_only=True):
        result = local('python3 -m pytest tests', capture=True)
    if result.failed and not confirm('Tests failed. Continue anyway?'):
        abort('Aborting at user request.')


def commit():
    with settings(warn_only=True):
        local('git add -i && git commit')


def push(branch):
    local('git push origin %s' % branch)


@task
def prepare_deploy(branch):
    test()
    commit()
    push(branch)
