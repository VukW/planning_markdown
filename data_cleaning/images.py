from PIL import Image
from os.path import join
import numpy as np
import pandas as pd
from PIL.ImageOps import invert
from utils import draw_points

TRANSFORMED_IMAGES_FOLDER = '../images'
CORNER_RADIUS = 32  # neighbourhood of this radius is taken for each corner point
FINAL_RADIUS = 12  # corners are resized to this radius (to decrease dimensionality)
CORNERS_TRANSFORMATIONS = 6  # data augmentation. Each corner is randomly transformed this times
FLAT_CORNER_COSINE = -0.1  # if the cosine between two edges is lower, then angle is flat
BLACK_THRESHOLD = 192  # we left only pixels darker than this
EDGE_WIDTH = 20
EDGE_FINAL_WIDTH = 12
EDGE_FINAL_LENGTH = 30
IS_EDGE_ALLOWED_THRESHOLD = 1.02
EDGE_TRANSFORMATIONS = 2

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


def get_corner_label(corner_no, corners, edges):
    """calculates class of the corner based on the edges
    classes:
    1 - flat corner (where two neighbours and angle > 90)
    2 - one-neighboured corner
    ...
    N+1 - N-neighboured corner
    """
    if len(edges[corner_no]) != 2:
        return len(edges[corner_no]) + 1

    # check if angle is flat: cosine(AB, BC) < -THRESHOLD
    b = np.array(corners[corner_no])
    a = np.array(corners[edges[corner_no][0]])
    c = np.array(corners[edges[corner_no][1]])

    vect_ab = b - a
    vect_bc = c - b
    if np.dot(vect_ab, vect_bc) < FLAT_CORNER_COSINE * np.linalg.norm(vect_ab) * np.linalg.norm(vect_bc):
        return 1  # the corner is flat
    else:
        return 3  # 2-neighboured class


def clean_image(image):
    data = np.array(image.getdata()).reshape(image.size[::-1]).astype('uint8')
    data[data > BLACK_THRESHOLD] = 255
    return Image.fromarray(data, mode='L')


def white_bordered_image(image, border_size):
    white_filled = Image.new('L',
                             (image.size[0] + 2 * border_size,
                              image.size[1] + 2 * border_size),
                             color=255)
    white_filled.paste(image, (border_size, border_size))
    return white_filled


class BaseDataFrameClassifier:
    """template for classifying """
    def __init__(self, data_size):
        np.random.seed(514229)
        self.step = 1000
        self.data_size = data_size
        self.data = self.empty_data_chunk()
        self.df = []  # now it is just list; we will convert it to pd.df later
        self.next_idx_ = 0

    def empty_data_chunk(self):
        return np.zeros((self.step, self.data_size), dtype=np.uint8)

    def next_idx(self):
        if self.data.shape[0] <= self.next_idx_:
            self.data = np.vstack((self.data, self.empty_data_chunk()))
        self.next_idx_ += 1
        return self.next_idx_ - 1

    def save(self, filename):
        pd.DataFrame(self.df).to_csv(filename, index=False)
        np.save(filename + '.data', self.data[:self.next_idx_])


class DataFrameForCornersClassifier(BaseDataFrameClassifier):
    def __init__(self):
        super().__init__(data_size=4 * FINAL_RADIUS ** 2)

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
        white_filled = white_bordered_image(image, border_size)

        for ic, corner_old in enumerate(corners):
            # print('corner', corner_old)
            corner = (corner_old[0] + border_size,
                      corner_old[1] + border_size)
            corner_base = {'image_id': image_id,
                           'source_x': corner[0],
                           'source_y': corner[1],
                           'image_width': image.size[0],
                           'image_height': image.size[1],
                           'label': get_corner_label(ic, corners, edges)}

            # add original corner
            corner_row = corner_base.copy()
            corner_row['source_corner_height'] = CORNER_RADIUS * 2
            corner_row['source_corner_width'] = CORNER_RADIUS * 2
            corner_row['angle'] = 0
            corner_row['offset_x'] = 0
            corner_row['offset_y'] = 0
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
                corner_row['offset_x'] = int(random_offset_coeff(CORNER_RADIUS / 5))
                corner_row['offset_y'] = int(random_offset_coeff(CORNER_RADIUS / 5))
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


def edge_extract(image: Image, point_from: tuple, point_to: tuple, edge_width: int):
    edge = image.crop((min(point_from[0], point_to[0]) - 2 * edge_width,
                       min(point_from[1], point_to[1]) - 2 * edge_width,
                       max(point_from[0], point_to[0]) + 2 * edge_width,
                       max(point_from[1], point_to[1]) + 2 * edge_width,
                       ))
    vect_edge = np.array(point_from) - np.array(point_to)
    edge_len = np.linalg.norm(vect_edge)
    angle = np.arccos(np.dot(vect_edge, [0, 1]) / edge_len) * 180 / np.pi
    # we don't know if we should rotate on +angle or -angle.
    # if angle between vect and OX is < 90, then we 'll rotate on +angle;
    # else, on -angle
    if np.dot(vect_edge, [1, 0]) < 0:
        angle = -angle
    edge = invert(edge)
    edge = edge.rotate(angle=angle, expand=True)
    edge = invert(edge)
    new_center = np.array(edge.size) // 2
    edge = edge.crop((new_center[0] - edge_width / 2,
                      new_center[1] - int(edge_len / 2),
                      new_center[0] + edge_width / 2,
                      new_center[1] + int(edge_len / 2)))
    return edge


def check_if_edge(start: int, end: int, corners: list, edges: dict) -> bool:
    """
    solves if there is a single wall connecting this two corners. The problem is that wall may consist of
    multiple edges
    Implements Dijkstra algorithm for finding the shortest path
    :param start: corner1 number
    :param end: corner2 number
    :param corners: corner coordinates
    :param edges: list of connecting edges
    :return: boolean: True / False
    """

    def line_len(start_corner: int, end_corner: int):
        return np.sqrt((corners[start_corner][0] - corners[end_corner][0]) ** 2 +
                       (corners[start_corner][1] - corners[end_corner][1]) ** 2)

    # simple check: maybe there is one direct edge
    if end in edges[start]:
        return True

    FAKE_DISTANCE = 1e15
    # the nodes are connected if distance between them is almost the same as the direct distance

    direct_distance = line_len(start, end)

    distances = [FAKE_DISTANCE] * len(corners)
    distances[start] = 0
    marked = [False] * len(corners)

    while True:
        # find the unmarked corner with the smallest distance
        current_corner = None
        min_distance = FAKE_DISTANCE
        for ic, dist_ in enumerate(distances):
            if (not marked[ic]) and (dist_ < min_distance):
                min_distance = dist_
                current_corner = ic

        if current_corner is None:
            # no unmarked corners within start component
            return False

        if min_distance > direct_distance * IS_EDGE_ALLOWED_THRESHOLD:
            # we are already too far from the start point
            return False

        if current_corner == end:
            # the distance is less and we already finished
            return True

        # graph walking
        for next_corner in edges[current_corner]:
            distances[next_corner] = min(distances[next_corner],
                                         min_distance + line_len(current_corner, next_corner))

        marked[current_corner] = True


class DataFrameForEdgesClassifier(BaseDataFrameClassifier):
    def __init__(self):
        super().__init__(data_size=EDGE_FINAL_LENGTH * EDGE_FINAL_WIDTH)

    def append_rotated_4_directions(self, edge_row, edge_array_2d):
        edge_array_app = edge_array_2d.copy()
        for direction in range(4):
            edge_row_app = edge_row.copy()
            edge_row_app['direction'] = direction

            row_idx = self.next_idx()
            self.data[row_idx] = edge_array_app.reshape(-1)
            self.df.append(edge_row_app)
            if direction == 1:
                # mirror corner
                edge_array_app = edge_array_app[::-1, :]
            else:
                edge_array_app = edge_array_app[:, ::-1]
            del edge_row_app
        del edge_array_app

    def append(self, image, image_id, corners, edges):
        """
        appends every edge to df
        :param image: Image object
        :param image_id: id of image, saved to df
        :param corners: list of corner points: [(x1,y1), .., (xn,yn)]
        :param edges: dict of edges: {0:[1,2,3], ..}
        :return: None
        """
        border_size = 2 * CORNER_RADIUS
        white_filled = white_bordered_image(image, border_size)

        bordered_corners = np.array(corners) + (border_size, border_size)

        for ic, point_from in enumerate(bordered_corners):
            # print('corner', corner_old)
            for jc, point_to in enumerate(bordered_corners[ic + 1:], start=ic + 1):
                if check_if_edge(ic, jc, corners, edges):
                    right_answer = 1
                else:
                    right_answer = 0

                edge_base = {'image_id': image_id,
                             'source_start_x': point_from[0],
                             'source_start_y': point_from[1],
                             'source_end_x': point_to[0],
                             'source_end_y': point_to[1],
                             'image_width': image.size[0],
                             'image_height': image.size[1],
                             'label': right_answer}

                # add original edge
                for _ in range(EDGE_TRANSFORMATIONS):
                    edge_row = edge_base.copy()
                    edge_row['source_edge_len'] = np.linalg.norm(np.array(point_to) - np.array(point_from))
                    if _ == 0:
                        edge_width = EDGE_WIDTH
                    else:
                        edge_width = int(EDGE_WIDTH * random_scale_coeff(0.9, 2))
                    edge_row['source_edge_width'] = edge_width
                    edge_image = edge_extract(white_filled,
                                              point_from,
                                              point_to,
                                              edge_width=edge_width)
                    edge_image = edge_image.resize((EDGE_FINAL_WIDTH,
                                                    EDGE_FINAL_LENGTH))
                    edge_array = np.array(edge_image.getdata()).reshape(edge_image.size[::-1])  # h,w
                    # print('edge received, ', edge_array.shape)
                    self.append_rotated_4_directions(edge_row, edge_array)

                    del edge_row
                    del edge_image
                    del edge_array

        del bordered_corners
        del white_filled
