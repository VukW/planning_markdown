from PIL import Image
from os.path import join
import numpy as np

TRANSFORMED_IMAGES_FOLDER = '../images'
HARDCODED_HEIGHT = 600
HARDCODED_WIDTH = 800
CORNER_RADIUS = 32


def save_image(image, image_id):
    image.save(join(TRANSFORMED_IMAGES_FOLDER,
                    image_id+'.png'), "PNG")


def save_corners(image, image_id, corners):
    # 1. save alpha
    width, height = image.size
    image_alpha = np.zeros(shape=(height, width))
    for ic, corner in enumerate(corners):
        left = max(0, corner[0] - CORNER_RADIUS)
        right = min(width, corner[0] + CORNER_RADIUS)
        up = max(0, corner[1] - CORNER_RADIUS)
        bottom = min(height, corner[1] + CORNER_RADIUS)
        image_alpha[up:bottom, left:right] = 255
        image.crop((left, up, right, bottom)).save(join(TRANSFORMED_IMAGES_FOLDER,
                                                        image_id+'-'+str(ic)+'.png'), "PNG")
    Image.fromarray(image_alpha.astype('uint8'), mode='L').save(join(TRANSFORMED_IMAGES_FOLDER,
                                                                     image_id+'-alpha.png'), "PNG")


def transform_corners(corners, borders):
    width_prop = (borders['right_border']-borders['left_border'])/HARDCODED_WIDTH
    height_prop = (borders['bottom_border']-borders['up_border'])/HARDCODED_HEIGHT
    new_corners = [(int(c[0]*width_prop), int(c[1]*height_prop)) for c in corners]
    return new_corners
