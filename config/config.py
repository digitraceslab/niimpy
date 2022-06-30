import configparser
import os 

cwd = os.path.dirname(__file__)
config_ini = os.path.join(cwd, 'config.ini')

config = configparser.ConfigParser()
config.read(config_ini)

ROOT = os.path.dirname(os.path.dirname(__file__))
SAMPLE_DATA = config['sample_paths']['sample_data']
MULTIUSER_AWARE_BATTERY_PATH =  os.path.join(ROOT, config['sample_paths']['multiuser_aware_battery'])
MULTIUSER_AWARE_SCREEN_PATH = os.path.join(ROOT, config['sample_paths']['multiuser_aware_screen'])
STEP_SUMMARY_PATH = os.path.join(ROOT, config['sample_paths']['step_summary'])
GPS_PATH =  os.path.join(ROOT, config['sample_paths']['gps'])
SURVEY_PATH = os.path.join(ROOT, config['sample_paths']['survey'])
SQLITE_SINGLEUSER_PATH =os.path.join(ROOT, config['sample_paths']['sqlite_singleuser']) 
SQLITE_MULTIUSER_PATH =os.path.join(ROOT, config['sample_paths']['sqlite_multiuser']) 