import configparser
import os 

cwd = os.path.dirname(__file__)
config_ini = os.path.join(cwd, 'config.ini')

config = configparser.ConfigParser()
config.read(config_ini)

ROOT = config['sample_paths']['root']
SAMPLE_DATA = config['sample_paths']['sample_data']
MULTIUSER_AWARE_BATTERY_PATH = config['sample_paths']['multiuser_aware_battery']
MULTIUSER_AWARE_SCREEN_PATH = config['sample_paths']['multiuser_aware_screen']
STEP_SUMMARY_PATH = config['sample_paths']['step_summary']
GPS_PATH = config['sample_paths']['gps']