from PIL import Image
from os.path import join
import numpy as np
import pandas as pd
from PIL.ImageOps import invert

TRANSFORMED_IMAGES_FOLDER = '../images'
CORNER_RADIUS = 32
FINAL_RADIUS = 12
CORNERS_TRANSFORMATIONS = 5


def save_image(image, image_id):
    image.save(join(TRANSFORMED_IMAGES_FOLDER,
                    image_id + '.png'), "PNG")


def save_corners(image, image_id, corners):
    # 1. save alpha. I'm not sure i really need it
    width, height = image.size
    image_alpha = np.zeros(shape=(height, width))
    for ic, corner in enumerate(corners):
        left = max(0, corner[0] - CORNER_RADIUS)
        right = min(width, corner[0] + CORNER_RADIUS)
        up = max(0, corner[1] - CORNER_RADIUS)
        bottom = min(height, corner[1] + CORNER_RADIUS)
        image_alpha[up:bottom, left:right] = 255

        image.crop((left, up, right, bottom)).save(join(TRANSFORMED_IMAGES_FOLDER,
                                                        image_id + '-' + str(ic) + '.png'), "PNG")
    Image.fromarray(image_alpha.astype('uint8'), mode='L').save(join(TRANSFORMED_IMAGES_FOLDER,
                                                                     image_id + '-alpha.png'), "PNG")


def transform_corners(corners, borders, real_size):
    width, height = real_size
    width_prop = (borders['right_border'] - borders['left_border']) / width
    height_prop = (borders['bottom_border'] - borders['up_border']) / height
    new_corners = [(int(c[0] * width_prop + width / 2), int(c[1] * height_prop + height / 2)) for c in corners]
    return new_corners


def random_scale_coeff(from_, to_):
    """ generates random scale coefficient, median at 1; exponential
    :param from_:  0.5
    :param to_: 1.5
    :return:
    """
    basic_coeff = 2 ** np.clip(np.random.normal() / 4, -0.75, 0.75)
    basic_min = 2 ** (-0.75)
    basic_max = 2 ** 0.75
    old_scale = basic_max - basic_min
    new_scale = to_ - from_
    return (basic_coeff - basic_min) * new_scale / old_scale + from_


def random_offset_coeff(max_):
    """
    normal symmetric, clipped
    :param max_: maximum amplitude
    :return: coeff
    """
    return np.clip(np.random.normal() / 3, -1, 1) * max_


def corner_randomly_transform(image, corner,
                              offset_x=0, offset_y=0,
                              x_radius=CORNER_RADIUS,
                              y_radius=CORNER_RADIUS,
                              angle=0):
    draft_radius = int(np.sqrt(x_radius ** 2 + y_radius ** 2) + 2)
    # 1. offset
    real_corner = (corner[0] + offset_x, corner[1] + offset_y)
    draft_image = image.crop((real_corner[0] - draft_radius,
                              real_corner[1] - draft_radius,
                              real_corner[0] + draft_radius,
                              real_corner[1] + draft_radius))
    # 2. rotate. It fills borders black; so we need invert it twice
    draft_image = invert(invert(draft_image).rotate(angle, expand=1))

    # 3. crop corner
    corner_image = draft_image.crop((draft_image.size[0] // 2 - x_radius,
                                     draft_image.size[1] // 2 - y_radius,
                                     draft_image.size[0] // 2 + x_radius,
                                     draft_image.size[1] // 2 + y_radius))

    # scale
    return corner_image.resize((FINAL_RADIUS * 2, FINAL_RADIUS * 2))


class DataFrameForClassifier:
    def __init__(self):
        np.random.seed(514229)
        self.step = 1000
        # self.pxs = ['px' + str(_) for _ in range(4 * CORNER_RADIUS ** 2)]
        self.data = self.empty_data_chunk()
        # self.df = pd.DataFrame(columns=(['image_id',
        #                                  'image_width',
        #                                  'image_height',
        #                                  'source_x',
        #                                  'source_y',
        #                                  'source_corner_height',
        #                                  'source_corner_width',
        #                                  'angle',
        #                                  'direction',
        #                                  'offset_x',
        #                                  'offset_y'] +
        #                                 self.pxs +
        #                                 ['label']))
        self.df = []  # now it is just list; we will convert it to pd.df later
        self.next_idx_ = 0

    def empty_data_chunk(self):
        return np.zeros((self.step, 4*FINAL_RADIUS**2), dtype=np.uint8)

    def next_idx(self):
        if self.data.shape[0] <= self.next_idx_:
            self.data = np.vstack((self.data, self.empty_data_chunk()))
        self.next_idx_ += 1
        return self.next_idx_ - 1

    def append_rotated_8_directions(self, corner_row, corner_array_2d):
        corner_array_app = corner_array_2d.copy()
        for direction in range(8):
            corner_row_app = corner_row.copy()
            corner_row_app['direction'] = direction
            # corner_row_app.update(dict(zip(self.pxs, corner_array_app.reshape(-1))))
            row_idx = self.next_idx()
            self.data[row_idx] = corner_array_app.reshape(-1)
            self.df.append(corner_row_app)
            corner_array_app = corner_array_app.T[:, ::-1]
            if direction == 4:
                # mirror corner
                corner_array_app = corner_array_app[:, ::-1]
            del corner_row_app
        del corner_array_app

    def append(self, image, image_id, corners, edges):
        # add white borders to image
        # print('appending image', image_id)
        border_size = 2 * CORNER_RADIUS
        white_filled = Image.new('L',
                                 (image.size[0] + 2 * border_size,
                                  image.size[1] + 2 * border_size),
                                 color=255)
        white_filled.paste(image, (border_size, border_size))
        for corner_old in corners:
            # print('corner', corner_old)
            corner = (corner_old[0] + border_size,
                      corner_old[1] + border_size)
            corner_base = {'image_id': image_id,
                           'source_x': corner[0],
                           'source_y': corner[1],
                           'image_width': image.size[0],
                           'image_height': image.size[1]}

            corner_row = corner_base.copy()
            corner_row['source_corner_height'] = CORNER_RADIUS * 2
            corner_row['source_corner_width'] = CORNER_RADIUS * 2
            corner_row['angle'] = 0
            corner_row['offset_x'] = 0
            corner_row['offset_y'] = 0
            corner_row['label'] = 1
            corner_image = corner_randomly_transform(white_filled, corner)
            corner_array = np.array(corner_image.getdata()).reshape(corner_image.size[::-1])  # h,w
            # print('corner received, ', corner_array.shape)
            self.append_rotated_8_directions(corner_row, corner_array)

            del corner_row
            del corner_image
            del corner_array

            for _ in range(CORNERS_TRANSFORMATIONS):
                # print('corner transformations', _)
                # случайная трансформация
                corner_row = corner_base.copy()
                corner_row['source_corner_height'] = int(CORNER_RADIUS * 2 * random_scale_coeff(0.5, 1.5))
                corner_row['source_corner_width'] = int(CORNER_RADIUS * 2 * random_scale_coeff(0.5, 1.5))
                corner_row['angle'] = random_offset_coeff(45)
                corner_row['offset_x'] = int(random_offset_coeff(CORNER_RADIUS / 2))
                corner_row['offset_y'] = int(random_offset_coeff(CORNER_RADIUS / 2))
                corner_row['label'] = 1
                corner_image = corner_randomly_transform(white_filled,
                                                         corner,
                                                         offset_x=corner_row['offset_x'],
                                                         offset_y=corner_row['offset_y'],
                                                         x_radius=corner_row['source_corner_width'] // 2,
                                                         y_radius=corner_row['source_corner_height'] // 2,
                                                         angle=corner_row['angle'])
                corner_array = np.array(corner_image.getdata()).reshape(corner_image.size[::-1])
                self.append_rotated_8_directions(corner_row, corner_array)
                del corner_row
                del corner_image
                del corner_array

        # add not-a-corners
        corner_base = {'image_id': image_id,
                       'image_width': image.size[0],
                       'image_height': image.size[1]}

        not_a_corners = 0
        # add not-a-corner for each edge (random point)
        for point_from in edges:
            for point_to in edges[point_from]:
                if point_from >= point_to:
                    continue
                edge_start = np.array(corners[point_from])
                edge_end = np.array(corners[point_to])
                edge_vect = edge_end - edge_start
                edge_len = np.linalg.norm(edge_vect)
                if edge_len < CORNER_RADIUS * 2:
                    continue
                t = np.random.rand() * (edge_len - CORNER_RADIUS * 2) + CORNER_RADIUS
                random_point = np.round(edge_start + edge_vect * t / edge_len)
                corner_row = corner_base.copy()
                corner_row['source_x'] = random_point[0]
                corner_row['source_y'] = random_point[1]
                corner_row['source_corner_width'] = CORNER_RADIUS
                corner_row['source_corner_height'] = CORNER_RADIUS
                corner_row['angle'] = 0
                corner_row['offset_x'] = 0
                corner_row['offset_y'] = 0
                corner_row['label'] = 0
                corner_image = corner_randomly_transform(white_filled,
                                                         random_point)
                corner_array = np.array(corner_image.getdata()).reshape(corner_image.size[::-1])
                self.append_rotated_8_directions(corner_row, corner_array)
                not_a_corners += 1
                del corner_row
                del corner_array
                del corner_image

        while not_a_corners < len(corners) * (CORNERS_TRANSFORMATIONS + 1):
            random_point = np.array([np.random.randint(image.size[0]),
                                     np.random.randint(image.size[1])])
            # check that point is far enough from real corners
            if np.min(np.apply_along_axis(lambda p: np.linalg.norm(random_point - p),
                                          1,
                                          corners)) < CORNER_RADIUS:
                continue
            # check that point has enough info

            if (np.array(white_filled
                                 .crop((random_point[0] - CORNER_RADIUS,
                                        random_point[1] - CORNER_RADIUS,
                                        random_point[0] + CORNER_RADIUS,
                                        random_point[1] + CORNER_RADIUS))
                                 .getdata())
                        .reshape((CORNER_RADIUS * 2, CORNER_RADIUS * 2))
                        .mean()) < 255 * 0.05:  # at least 5% of the area should be filled
                continue
            corner_row = corner_base.copy()
            corner_row['source_x'] = random_point[0]
            corner_row['source_y'] = random_point[1]
            corner_row['source_corner_width'] = CORNER_RADIUS
            corner_row['source_corner_height'] = CORNER_RADIUS
            corner_row['angle'] = 0
            corner_row['offset_x'] = 0
            corner_row['offset_y'] = 0
            corner_row['label'] = 0
            corner_image = corner_randomly_transform(white_filled,
                                                     random_point)
            corner_array = np.array(corner_image.getdata()).reshape(corner_image.size[::-1])
            self.append_rotated_8_directions(corner_row, corner_array)
            not_a_corners += 1
            del corner_row
            del corner_array
            del corner_image
        del white_filled

    def save(self, filename):
        pd.DataFrame(self.df).to_csv(filename, index=False)
        np.save(filename + '.data', self.data[:self.next_idx_])
