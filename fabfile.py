from getpass import getpass
from io import StringIO

from fabric.api import settings, local, abort, run, cd, env, prefix, sudo, prompt, put
from fabric.contrib.console import confirm 

env.sources_directory = '/var/www/meetup-facebook-bot'
env.socket_path = '/tmp/meetup-facebook-bot.socket'
env.venv_folder = 'venv'
env.venv_directory = '%s/%s' % (env.sources_directory, env.venv_folder)
env.venv_activate_command = 'source %s/bin/activate' % env.venv_directory
env.app_ini_filepath = '%s/meetup-facebook-bot.ini' % env.sources_directory
env.uwsgi_service_file_name = 'meetup_facebook_bot.service'
env.ssl_params_path = '/etc/nginx/snippets/ssl-params.conf'


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
    run('echo "0 */12 * * * systemctl restart nginx" | sudo tee --append /etc/crontab')


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


def create_uwsgi_service_file():
    put(StringIO(
u'''[Unit]
Description=uWSGI instance to serve meetup_facebook_bot
After=network.target

[Service]
User={user}
Group=www-data
WorkingDirectory={work_dir}
Environment="PATH={env_bin_dir}"
ExecStart={uwsgi_path} --ini {app_ini_path}

[Install]
WantedBy=multi-user.target'''.format(
                user=env.user,
                work_dir=env.sources_directory,
                env_bin_dir='%s/bin' % env.venv_directory,
                uwsgi_path = '%s/bin/uwsgi' % env.venv_directory,
                app_ini_path=env.app_ini_filepath
            )
        ),
        '/etc/systemd/system/%s' % env.uwsgi_service_file_name,
        use_sudo=True
    )


def start_uwsgi_service():
    sudo('systemctl daemon-reload')
    sudo('systemctl start %s' % env.uwsgi_service_file_name)


def create_ssl_params_file():
    dhparam_path = '/etc/ssl/certs/dhparam.pem'
    with settings(warn_only=True):
        dhparam_existence_check = run('test -f %s' % dhparam_path)
    if dhparam_existence_check.succeeded:
        print('dhparam file exists, skipping this step')
        return;
    sudo('openssl dhparam -out %s 2048' % dhparam_path)
    put(StringIO(
        u'''# from https://cipherli.st/
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
ssl_prefer_server_ciphers on;
ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
ssl_ecdh_curve secp384r1;
ssl_session_cache shared:SSL:10m;
ssl_session_tickets off;
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
# Disable preloading HSTS for now.  You can use the commented out header line that includes
# the "preload" directive if you understand the implications.
#add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
ssl_dhparam {dhparam_path};'''.format(
                dhparam_path=dhparam_path,
            )
        ),
        env.ssl_params_path,
        use_sudo=True
    )


def remove_trailing_slash_if_present(path):
    return path[:-1] if path[-1] == '/' else path

def configure_letsencrypt():
    sudo("mkdir -p /tmp/git")
    sudo("rm -rf /tmp/git/letsencrypt")
    with cd("/tmp/git"):
        sudo("git clone https://github.com/letsencrypt/letsencrypt")
    with cd("/tmp/git/letsencrypt"):
        run('./letsencrypt-auto certonly --standalone')
    sudo('rm -rf /tmp/git')
    env.letsnecrypt_folder = remove_trailing_slash_if_present(
        prompt('What\'s your letsencrypt directory? (e.g. /etc/letsencrypt/live/example.com)')
    )
    print('OK, it\'s %s' % env.letsnecrypt_folder)
    create_ssl_params_file()


def create_nginx_config():
    if not hasattr(env, 'domain_name'):
        env.domain_name = prompt('Enter your domain name:', default='metup_facebook_bot')
    nginx_config_path = '/etc/nginx/sites-available/%s' % env.domain_name
    put(StringIO(
        u'''server {{
    listen 80;
    listen [::]:80;

    server_name {domain};
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    include {ssl_params_path};

    ssl_certificate {fullchain_path};
    ssl_certificate_key {privkey_path};

    root {source_dir}
    index index.html index.htm index.nginx-debian.html;

    location / {{
        include uwsgi_params;
        uwsgi_pass unix:{socket_path};
    }}
}}'''.format(
                source_dir=env.sources_directory,
                domain=env.domain_name,
                ssl_params_path=env.ssl_params_path,
                fullchain_path='%s/fullchain.pem' % env.letsnecrypt_folder,
                privkey_path='%s/privkey.pem' % env.letsnecrypt_folder,
                socket_path=env.socket_path
            )
        ),
        nginx_config_path,
        use_sudo=True
    )
    nginx_config_alias = '/etc/nginx/sites-enabled/%s' % env.domain_name
    sudo('ln -s %s %s' % (nginx_config_path, nginx_config_alias))


def start_nginx():
    sudo('systemctl restart nginx')


def run_setup_scripts():
    # setup database and get_started button
    pass


def prepare_machine():
    pass
