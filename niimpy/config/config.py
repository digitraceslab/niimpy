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
MULTIUSER_AWARE_CALLS_PATH = os.path.join(ROOT,config['sample_paths']['multiuser_aware_calls'])
MULTIUSER_AWARE_MESSAGES_PATH = os.path.join(ROOT,config['sample_paths']['multiuser_aware_messages'])
MULTIUSER_AWARE_AUDIO_PATH = os.path.join(ROOT,config['sample_paths']['multiuser_aware_audio'])
SINGLEUSER_AWARE_APP_PATH = os.path.join(ROOT,config['sample_paths']['singleuser_aware_application'])
STEP_SUMMARY_PATH = os.path.join(ROOT, config['sample_paths']['step_summary'])
GPS_PATH =  os.path.join(ROOT, config['sample_paths']['gps'])
SURVEY_PATH = os.path.join(ROOT, config['sample_paths']['survey'])
SL_ACTIVITY_PATH = os.path.join(ROOT, config['sample_paths']['studentlife_activity'])
SQLITE_SINGLEUSER_PATH =os.path.join(ROOT, config['sample_paths']['sqlite_singleuser']) 
SQLITE_MULTIUSER_PATH =os.path.join(ROOT, config['sample_paths']['sqlite_multiuser']) 

MHEALTH_TOTAL_SLEEP_TIME_PATH = os.path.join(ROOT, config['sample_paths']['mhealth_total_sleep_time'])
MHEALTH_HEART_RATE_PATH = os.path.join(ROOT, config['sample_paths']['mhealth_heart_rate'])
MHEALTH_GEOLOCATION_PATH = os.path.join(ROOT, config['sample_paths']['mhealth_geolocation'])

GOOGLE_TAKEOUT_PATH = os.path.join(ROOT, config['sample_paths']['google_takeout'])
GOOGLE_TAKEOUT_DIR = os.path.join(ROOT, config['sample_paths']['google_takeout_dir'])
