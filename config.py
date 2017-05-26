PORT = 8000
DEBUG = True

# =======================================
# WEB-SERVICE
# =======================================
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


# ============================================
# CORNERS-CLEANING
# ============================================
CLEAN_SAVE_TRANSFORMED_IMAGES_FOLDER = '../images'
CLEAN_SAVE_CLUSTERED_GRAPH = DB_FILE_PATH + '.clustered'
CLEAN_SAVE_CLUSTERED_GRAPH_FOR_WEB_SERVICE = DB_FILE_PATH + '-cleaned.json'
CLEAN_SAVE_CORNERS_DF = DB_FILE_PATH + '-corners-df.csv'
CLEAN_SAVE_EDGES_DF = DB_FILE_PATH + '-eges-df.csv'
# also date numpy arrays are saved at (SAVE_%SMTH%_DF + '.data.npy')

# =============
# image cleaning
BLACK_THRESHOLD = 192  # we left only pixels darker than this
BORDER_SIZE = 64

# =============
# corners
CORNER_RADIUS = 32  # neighbourhood of this radius is taken for each corner point
CORNER_FINAL_RADIUS = 12  # corners are resized to this radius (to decrease dimensionality)
CORNERS_TRANSFORMATIONS_NUM = 6  # data augmentation. Each corner is randomly transformed this times
CORNER_FLAT_COSINE = -0.1  # if the cosine between two edges is lower, then angle is flat
CORNER_0_CLASS_BLACK_PROP = 0.05  # for not-a-corners we take only points with not less than of black pixels
CORNER_RANDOM_SCALE = [0.5, 1.5]
CORNER_RANDOM_ROTATE = 45
CORNER_RANDOM_OFFSET = CORNER_RADIUS / 5
CORNER_SIZE = CORNER_RADIUS * 2
CORNER_FINAL_SIZE = CORNER_FINAL_RADIUS * 2

# =============
# edges
EDGE_WIDTH = 20
EDGE_FINAL_WIDTH = 12
EDGE_FINAL_LENGTH = 30
IS_EDGE_ALLOWED_THRESHOLD = 1.02
EDGE_TRANSFORMATIONS_NUM = 2
EDGE_RANDOM_SCALE = [0.9, 2]


# ============================================
# MODELS PREDICTION
# ============================================
MODELS_SAVE_PREDICTION = DB_FILE_PATH + '-predicted.json'
# =============
# corners
MODELS_CORNERS_THRESHOLD = 0.98
MODELS_CORNERS_MODEL = "models/keras_cifar_corners.model"
MODELS_CLUSTERING_DIST = 5
# =============
# edges
MODELS_EDGES_THRESHOLD = 0.88
MODELS_EDGES_MODEL = "models/keras_cifar_edges.model"


# ============================================
# loading local config (if exists)
# ============================================
try:
    from local_config import *
except ImportError:
    pass
