PORT = 8000

OBJECT_TYPES = [{'name': 'my_point',
                 'color': '#00FF00',
                 'basic_type': 'POINT'},
                {'name': 'my_segment',
                 'color': '#FF0000',
                 'basic_type': 'SEGMENT'},
                {'name': 'my_region1',
                 'color': '#0000FF',
                 'basic_type': 'REGION'},
                {'name': 'my_region2',
                 'color': '#00CCCC',
                 'basic_type': 'REGION'}]

LOCKED_TIME_SECONDS = 600

# =============
# DB
DB_FILE_PATH = 'saved_markdowns.json'
DB_INIT_URLS_LIST = 'urls.txt'

# =============
# search optimal angle to rotate
ROTATION_RESIZING_LEVELS = [{'size': 100, 'angle_diff': 180},
                     {'size': 200, 'angle_diff': 5}]
ROTATION_N_TO_SPLIT = 10

# =============
# search borders to crop
CROP_MIN_MAX_GAP = 64
CROP_SIGNIFICANT_MEAN = 10

# =============
# loading local config (if exists)
try:
    from local_config import *
except ImportError:
    pass
