#pylint: disable=missing-docstring, invalid-name, line-too-long, unused-import
import random
from fabric.api import local, run, env, cd, sudo
from fabric.contrib.files import append, exists, sed

env.hosts = ['']
env.user = ''
env.key_filename = ['']
env.password = ''
env.connection_attempts = 5
env.colorize_errors = True
env.warn_only = True

REPO_URL = 'https://github.com/nikolovdeyan/py_TDD-With-Python.git'

def prod():
    env.site_name = 'prod_tdd-with-django'
    print('Production configuration applied.')

def staging():
    env.site_name = 'staging_tdd-with-django'
    print('Staging configuration applied.')

def status():
    site_name = env.site_name
    os_info = run('lsb_release -d', quiet=True)
    nginx_status = run('cat /etc/nginx/sites-available/{}'.format(site_name), quiet=True)
    gunicorn_status = run('cat /etc/systemd/system/gunicorn-{}.service'.format(site_name), quiet=True)

    print('\n\n\nSTATUS OF: {}@{}'.format(site_name, env.host))
    print('_' * 79, '\n')
    print('System Information:\n{}\n\n\n'.format(os_info))
    print(nginx_status, '\n\n')
    print(gunicorn_status, '\n\n')

def deploy():
    site_dir = '/home/{}/sites/{}'.format(env.user, env.site_name)
    source_dir = site_dir + '/source'
    allowed_hosts = env.host

    _create_or_update_dir_structure(site_dir)
    _get_latest_source(source_dir)
    _update_settings(source_dir, allowed_hosts)
    _update_virtualenv(source_dir)
    _update_static_files(source_dir)
    _update_database(source_dir)

def reset_services():
    sudo('systemctl daemon-reload')
    sudo('systemctl reload nginx')

def _create_or_update_dir_structure(site_dir):
    for subdir in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p {}/{}'.format(site_dir, subdir))

def _get_latest_source(source_dir):
    if exists(source_dir + '/.git'):
        run('cd {} && git fetch'.format(source_dir))
    else:
        run('git clone {} {}'.format(REPO_URL, source_dir))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {} && git reset --hard {}'.format(source_dir, current_commit))

def _update_settings(source_dir, allowed_hosts):
    settings_path = source_dir + '/superlists/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, 'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["{}"]'.format(allowed_hosts))
    secret_key_file = source_dir + '/superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefgijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, 'SECRET_KEY = "{}"'.format(key))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_dir):
    virtualenv_dir = source_dir + '/../virtualenv'
    if not exists(virtualenv_dir + '/bin/pip'):
        run('python3.6 -m venv {}'.format(virtualenv_dir))
    run('{}/bin/pip install -r {}/requirements.txt'.format(virtualenv_dir, source_dir))

def _update_static_files(source_dir):
    run('cd {} && ../virtualenv/bin/python manage.py collectstatic --noinput'.format(source_dir), quiet=True)

def _update_database(source_dir):
    run('cd {} && ../virtualenv/bin/python manage.py migrate --noinput'.format(source_dir))
