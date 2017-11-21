#pylint: disable=missing-docstring, invalid-name, line-too-long, unused-import
import os
import random
from contextlib import contextmanager
from fabric.api import local, run, env, cd, sudo, env, task
from fabric.contrib.files import append, exists, sed
import fab_env_conf as config

env.hosts = config.HOSTS
env.port = config.PORT
env.user = config.USERNAME
env.key_filename = config.KEYFILE
env.password = config.KEYPASS
env.site_name = ''

env.warn_only = False
env.connection_attempts = 5

def prod():
    env.site_name = 'prod_tdd-with-django'
    print('Production configuration applied.')

def staging():
    env.site_name = 'staging_tdd-with-django'
    print('Staging configuration applied.')


def status():
    print('_' * 79)
    if not env.site_name:
        print('MISSING ENVIRONMENT...\n\nUse "fab <env> <command>" to execute.\n')
        return

    site_dir = '/home/{}/sites/{}'.format(env.user, env.site_name)
    source_dir = site_dir + '/source'
    settings_path = source_dir + '/superlists/settings.py'
    site_name = env.site_name
    os_info = run('lsb_release -d', quiet=True)
    nginx_status = run('cat /etc/nginx/sites-available/{}'.format(site_name), quiet=True)
    gunicorn_status = run('cat /etc/systemd/system/gunicorn-{}.service'.format(site_name), quiet=True)
    debug_status = run("cat {} | egrep 'DEBUG = (True|False)'".format(settings_path), quiet=True)
    allowed_hosts = run("cat {} | egrep 'ALLOWED_HOSTS'".format(settings_path), quiet=True)

    run('set -o posix; set')

    print('\nSTATUS OF: {}@{}'.format(site_name, env.host))
    print('_' * 79, '\n')
    print('System Information:\n{}'.format(os_info))
    print('Django development server setting: {}'.format(debug_status))
    print('Django allowed hosts setting: {}'.format(allowed_hosts))
    print('\nNginx Configuration (/etc/nginx/sites-available/):')
    print('.' * 79, '\n{}'.format(nginx_status))
    print('.' * 79, '\n\n\n')
    print('\nGunicorn Configuration (/etc/systemd/system/sites-available/):')
    print('.' * 79, '\n{}'.format(gunicorn_status))
    print('.' * 79, '\n\n\n')

def undeploy():
    site_dir = '/home/{}/sites/{}'.format(env.user, env.site_name)
    source_dir = site_dir + '/source'
    sudo('pwd')


def deploy():
    if not env.site_name:
        print('Use deploy with environent like: "fab staging deploy"')

    site_dir = '/home/{}/sites/{}'.format(env.user, env.site_name)
    source_dir = site_dir + '/source'
    allowed_hosts = env.host

    _create_or_update_dir_structure(site_dir)
    _get_latest_source(source_dir)
    _update_settings(source_dir, allowed_hosts)
    _update_virtualenv(source_dir)
    _update_static_files(source_dir)
    _update_database(source_dir)

def _create_or_update_dir_structure(site_dir):
    """Prepare project directory structure."""
    for subdir in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p {}/{}'.format(site_dir, subdir))

def _get_latest_source(source_dir):
    """Fetch latest commit if repo available, else clone it."""
    if exists(source_dir + '/.git'):
        run('cd {} && git fetch'.format(source_dir))
    else:
        run('git clone {} {}'.format(config.REPO, source_dir))
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
