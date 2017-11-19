#pylint: disable=missing-docstring, invalid-name, line-too-long, unused-import
import random
from fabric.api import local, run, env, cd, sudo
from fabric.contrib.files import append, exists, sed

env.key_filename = ['c:/Users/Thoth/.ssh/id_rsa']
env.hosts = ['Thoth@192.168.0.66:10022']

REPO_URL = 'https://github.com/nikolovdeyan/py_TDD-With-Python.git'
SITE_NAME = 'staging_tdd-with-django'
APP_DIR = '/home/Thoth/sites/{}/source/'.format(SITE_NAME)

def deploy():
    site_dir = '/home/{}/sites/{}'.format(env.user, SITE_NAME)
    source_dir = site_dir + '/source'
    _create_directory_structure_if_necessary(site_dir)
    _get_latest_source(source_dir)
    _update_settings(source_dir, env.host)
    _update_virtualenv(source_dir)
    _update_static_files(source_dir)
    _update_database(source_dir)

def _create_directory_structure_if_necessary(site_dir):
    for subdir in ('database', 'static', 'virtualenv', 'source'):
        run('mkdir -p {}/{}'.format(site_dir, subdir))

def _get_latest_source(source_dir):
    if exists(source_dir + '/.git'):
        run('cd {} && git fetch'.format(source_dir))
    else:
        run('git clone {} {}'.format(REPO_URL, source_dir))
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd {} && git reset --hard {}'.format(source_dir, current_commit))

def _update_settings(source_dir, site_name):
    settings_path = source_dir + '/superlists/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path, 'ALLOWED_HOSTS = .+$',
        'ALLOWED_HOSTS = ["{}"]'.format(site_name))
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
    run('cd {} && ../virtualenv/bin/python manage.py collectstatic --noinput'.format(source_dir))

def _update_database(source_dir):
    run('cd {} && ../virtualenv/bin/python manage.py migrate --noinput'.format(source_dir))
