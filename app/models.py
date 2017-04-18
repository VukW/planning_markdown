from io import BytesIO

from app import db
import random
from PIL import ImageDraw, Image, ImageFont
from PIL.ImageOps import invert
from urllib.request import urlopen
import numpy as np
from config import (CROP_MIN_MAX_GAP,
                    CROP_SIGNIFICANT_MEAN,
                    ROTATION_N_TO_SPLIT,
                    ROTATION_RESIZING_LEVELS)


def random_image(seed):
    random.seed(seed)
    width = random.randint(128, 1024 + 1)
    height = random.randint(128, 1024 + 1)
    img = Image.new('RGB', size=(width, height), color='white')
    rotate_direction = random.randint(0, 3)
    if rotate_direction in (0, 2):
        font_size = random.randrange(width // 25, width // 10)
    else:
        font_size = random.randrange(height // 25, height // 10)
    font = ImageFont.truetype("app/static/arial.ttf", size=font_size)
    txt = Image.new('RGB', (16 * font_size, int(1.1 * font_size)), color=(192, 192, 192))
    d = ImageDraw.Draw(txt)
    d.text((0, 0), "New image mock, generated by PIL", font=font, fill=0)
    rotated = txt.rotate(90 * rotate_direction, expand=1)
    img.paste(rotated, box=(random.randrange(width // 2),
                            random.randrange(height // 2)))
    d = ImageDraw.Draw(img)
    n_steps = random.randrange(10, 20)
    prev_point = [random.randrange(width), random.randrange(height)]
    prev_horizontal = True
    for _ in range(n_steps):
        next_dir = random.randint(0, 1)
        next_point = [0, 0]
        if prev_horizontal:
            next_point[0] = prev_point[0]
            if next_dir == 0:
                next_point[1] = random.randrange(prev_point[1] + 1)
            else:
                next_point[1] = random.randrange(prev_point[1] - 1, height)
        else:
            next_point[1] = prev_point[1]
            if next_dir == 0:
                next_point[0] = random.randrange(prev_point[0] + 1)
            else:
                next_point[0] = random.randrange(prev_point[0] - 1, width)
        prev_horizontal = not prev_horizontal
        d.line(prev_point + next_point, fill=0, width=3)
        prev_point = next_point
    return img


def load_image_from_url(url):
    img_io = urlopen(url).read()
    img = Image.open(BytesIO(img_io))
    return img


def resize_image(image, max_dimension):
    ratio = min(max_dimension / image.size[0], max_dimension / image.size[1])
    return image.resize((int(image.size[0] * ratio),
                         int(image.size[1] * ratio)),
                        Image.ANTIALIAS)


def rotate_image(image, angle=None):
    def rotating_criteria(image_to_rotate, angle):
        tmp_image = image_to_rotate.rotate(angle, expand=1)
        (width, height) = tmp_image.size
        image_array = np.array(tmp_image.getdata()).astype('uint8').reshape((height, width))
        # criteria = (np.max(np.sum(image_array, axis=0)) / height,
        #            np.max(np.sum(image_array, axis=1)) / width)
        criteria = [None, None]
        for axis in [0, 1]:
            # sum_over_axis = image_array.sum(axis=axis)
            # sum_over_axis = ((sum_over_axis[1:-1] > sum_over_axis[:-2]*10)
            #                 | (sum_over_axis[1:-1] > sum_over_axis[2:]*10))
            sum_over_axis = image_array.mean(axis=axis) > 5
            sum_over_axis = np.nonzero(sum_over_axis)[0]
            if len(sum_over_axis) > 0:
                criteria[axis] = sum_over_axis[-1] - sum_over_axis[0]
            else:
                criteria[axis] = 1000000
        # print('angle: ', angle, 'shape: ', image_array.shape, ', ', criteria)
        return min(criteria)

    print('basic image: ', image.size)

    if angle is None:
        # search optimal angle to rotate
        current_resize_level = 0
        angles = [-45.0]
        angles += [0] * (ROTATION_N_TO_SPLIT - 1)
        angles += [45.0]
        crit = [None] * (ROTATION_N_TO_SPLIT + 1)
        image_inverted = None
        while (angles[-1] - angles[0]) > 0.1:
            # отресайзим изображение, если надо
            if current_resize_level != len(ROTATION_RESIZING_LEVELS):
                if (angles[-1] - angles[0]) < ROTATION_RESIZING_LEVELS[current_resize_level]['angle_diff']:
                    image_inverted = resize_image(invert(image), ROTATION_RESIZING_LEVELS[current_resize_level]['size'])
                    current_resize_level += 1
                    print('image inverted: ', image_inverted.size)
                    crit[0] = rotating_criteria(image_inverted, angles[0])
                    crit[-1] = rotating_criteria(image_inverted, angles[-1])

            for ic in range(1, ROTATION_N_TO_SPLIT):
                angles[ic] = angles[0] + (angles[-1] - angles[0]) * ic / ROTATION_N_TO_SPLIT
                crit[ic] = rotating_criteria(image_inverted, angles[ic])
            max_point = (np.argmin(crit) + ROTATION_N_TO_SPLIT - np.argmin(crit[::-1])) // 2
            angles[0] = angles[max(max_point - 2, 0)]
            angles[-1] = angles[min(max_point + 2, ROTATION_N_TO_SPLIT)]
            crit[0] = crit[max(max_point - 2, 0)]
            crit[-1] = crit[min(max_point + 2, ROTATION_N_TO_SPLIT)]
            print('new borders: ', angles[0], angles[-1])
        max_point = (np.argmin(crit) + ROTATION_N_TO_SPLIT - np.argmin(crit[::-1])) // 2
        opt_angle = angles[max_point]
        opt_criteria = crit[max_point]

        # bruteforce
        # opt_angle = None
        # opt_criteria = 1000000
        # start = dt.now()
        # times = []
        # for angle in range(-45, 45, 1):
        #     crit = rotating_criteria(angle)
        #     if crit < opt_criteria:
        #         opt_criteria = crit
        #         opt_angle = angle
        #     times.append((dt.now() - start).total_seconds()*1000)
        #     start = dt.now()
        # print('time: {0:.3f}..{1:.3f}, mean = {2:.3f}'.format(np.min(times), np.max(times), np.mean(times)))

        print('opt_angle: ', opt_angle, ', criteria: ', opt_criteria)
    else:
        # take existing angle
        opt_angle = angle

    # final rotation
    if opt_angle != 0:
        tmp_image = image.rotate(opt_angle, expand=1)
        bg_mask = Image.new(mode='L', size=image.size, color=255).rotate(opt_angle, expand=1)
        bg = Image.new(mode='L', size=tmp_image.size, color=255)
        bg.paste(tmp_image, mask=bg_mask)
        return bg, opt_angle
    return image, 0


def crop_image(image, borders=None):
    print(image.size)
    width, height = image.size
    image_array = (np.ones(shape=(height, width), dtype='uint8') * 255
                   - np.array(image.getdata()).astype('uint8').reshape((height, width)))

    if borders is None:
        #  search optimal borders to crop
        hist_u_to_b = (((image_array.max(axis=1) - image_array.min(axis=1)) > CROP_MIN_MAX_GAP)
                       | (image_array.mean(axis=1) > CROP_SIGNIFICANT_MEAN))
        hist_l_to_r = (((np.max(image_array, axis=0) - np.min(image_array, axis=0)) > CROP_MIN_MAX_GAP)
                       | (np.mean(image_array, axis=0) > CROP_SIGNIFICANT_MEAN))
        print(hist_l_to_r.shape, hist_u_to_b.shape)
        left_border = int(max(np.nonzero(hist_l_to_r)[0][0] - 1, 0))
        right_border = int(min(np.nonzero(hist_l_to_r)[0][-1] + 1, width))
        up_border = int(max(np.nonzero(hist_u_to_b)[0][0] - 1, 0))
        bottom_border = int(min(np.nonzero(hist_u_to_b)[0][-1] + 1, height))
        borders = {'left_border': left_border,
                   'right_border': right_border,
                   'up_border': up_border,
                   'bottom_border': bottom_border}
    else:
        # take existing borders
        left_border = borders['left_border']
        right_border = borders['right_border']
        up_border = borders['up_border']
        bottom_border = borders['bottom_border']

    image_array = 255 - image_array[up_border:bottom_border, left_border:right_border]
    return Image.fromarray(image_array), borders


class ImageToMark:
    def __init__(self, image_id):
        self.image_id = image_id
        self._image = None

    @property
    def markdown(self):
        """planning markdown is saved here (redirection to database)"""
        return db[self.image_id]

    @markdown.setter
    def markdown(self, value):
        db[self.image_id] = value

    @property
    def image(self):
        if self._image is None:
            # self._image = random_image(self.image_id)
            self._image = load_image_from_url(self.url)
            # self._image = resize_image(self._image, 400)
            self._image = self._image.convert('L')  # to grayscale

            angle = db.get_full_item(self.image_id).get('angle', None)
            self._image, angle = rotate_image(self._image, angle = angle)  # optimal rotating
            db.get_full_item(self.image_id)['angle'] = angle

            borders = db.get_full_item(self.image_id).get('borders', None)
            self._image, borders = crop_image(self._image, borders = borders)
            db.get_full_item(self.image_id)['borders'] = borders

        return self._image

    @property
    def url(self):
        return db.get_full_item(self.image_id)['url']

    @property
    def duplicate(self):
        return db.get_full_item(self.image_id).get('duplicate', False)

    @duplicate.setter
    def duplicate(self, value):
        db.get_full_item(self.image_id)['duplicate'] = value


class ImagesToMark:
    def __init__(self):
        pass

    def __getitem__(self, item):
        return ImageToMark(item)
