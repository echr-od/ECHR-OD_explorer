import os
import yaml
import shutil
from datetime import datetime
import subprocess

from utils.config import config

TRANSITION_DIR = os.path.join(config()['data']['data_folder'], '{}.save'.format(config()['data']['build_name']))

def is_building_in_progress():
    lock = os.path.join(config()['data']['data_folder'], '.lock')
    return os.path.exists(lock)

def get_build_history():
    history_path = os.path.join(config()['data']['data_folder'], '.build_history')
    try:
        with open(history_path, 'r') as f:
            history = f.readlines()
        history = [e.split('::') for e in history]
    except Exception as e:
        print(e)
        history = [['never built', '']]
    return [dict(zip(['date', 'workflow'], e)) for e in history]

def get_latest_build():
    return get_build_history()[-1]

def get_build_info(build_name):
    current_build_info_path = os.path.join(config()['data']['data_folder'],
                                           build_name, 'build_info.yml')
    try:
        with open(current_build_info_path, 'r') as f:
            current_build_info = yaml.full_load(f)
        return current_build_info
    except Exception as e:
        return {}

def get_current_build():
    return get_build_info(config()['data']['build_name'])

def list_available_build():
    return [e for e in next(os.walk(config()['data']['data_folder']))[1] if os.path.isfile(os.path.join(config()['data']['data_folder'],
                                           e, 'build_info.yml'))]

def list_available_build_with_info():
    available_builds = list_available_build()
    info = {e: get_build_info(e) for e in available_builds}
    return info

def is_new_build_available():
    available_builds = list_available_build_with_info()
    current_build = get_current_build()
    current_build_date = datetime.strptime(current_build['build_time'], '%Y/%m/%d %H:%M:%S')
    available_builds = {k:v for k,v in available_builds.items() if k != available_builds[config()['data']['build_name']]}
    for build, info in available_builds.items():
        build_date = datetime.strptime(info['build_time'], '%Y/%m/%d %H:%M:%S')
        if build_date > current_build_date:
            return True, build
    return False, None

def update_build():
    available, new_build = is_new_build_available()
    if not available:
        return {'message': 'Build up-to-date'}
    if os.path.isdir(TRANSITION_DIR):
        shutil.rmtree(TRANSITION_DIR)
    current_build = os.path.join(config()['data']['data_folder'], config()['data']['build_name'])
    new_build_path = os.path.join(config()['data']['data_folder'], new_build)
    shutil.copytree(current_build, TRANSITION_DIR)
    shutil.rmtree(current_build)
    shutil.copytree(new_build_path, current_build)
    output = subprocess.run(["cat", "/proc/self/cgroup"], stdout=subprocess.PIPE)
    output = [e for e in output.stdout.decode().splitlines() if 'docker' in e]
    cid = output[-1].split('/')[-1]
    subprocess.run(["docker", "restart", cid])

    return {'message': 'Build updated'}