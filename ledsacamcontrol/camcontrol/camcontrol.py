import os
import subprocess
import re
from fractions import Fraction

def set_config(config):
    for configentry in config:
        subprocess.run(['gphoto2', '--set-config-value', f'{configentry}={config[configentry]}'])

def show_config(config):
    subprocess.run(["gphoto2", "--auto-detect"])
    for configentry in config:
        output = subprocess.check_output(['gphoto2', '--get-config', configentry])
        configvalue = output.decode("utf-8").split('Current:')[1].split('\n')[0]
        print(f"{configentry}:{configvalue}")

def capture_image_at_shutter_speed(shutter_speed, file):
    if os.path.exists(file):
        os.remove(file)
    subprocess.run(['gphoto2', '--set-config-value', f'Shutter Speed={shutter_speed}'])
    subprocess.run(['gphoto2', '--capture-image-and-download', '--filename', file])

def get_shutter_speed_list(local_images):
    if local_images == True:
        shutter_speed_list = open("shutter_speed_list.txt").readlines()
    else:
        output = subprocess.check_output(['gphoto2', '--get-config', 'Shutter Speed']).decode("utf-8")
        shutter_speed_list = re.findall(r'Choice: \d* (.*)\n', output)
        with open('shutter_speed_list.txt', 'w') as f:
            for item in shutter_speed_list:
                f.write(f"{item}\n")
    shutter_speed_list = [Fraction(index) for index in shutter_speed_list]
    return shutter_speed_list