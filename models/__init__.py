import keras
from PIL import Image
import numpy as np
from tqdm import tqdm

from config import CORNER_FINAL_SIZE, BORDER_SIZE
from data_cleaning.images import CORNER_RADIUS, white_bordered_image, edge_extract, EDGE_WIDTH, \
    EDGE_FINAL_WIDTH, EDGE_FINAL_LENGTH


def raw_list_of_points(data, threshold):
    """returns a list of points, that are predicted to be a corner"""
    return [point[::-1] for point in zip(*np.where(data > threshold))]


class ModelBase:
    def __init__(self, threshold):
        self.threshold = threshold

    def load(self, filename):
        self.model = keras.models.load_model(filename)


class ModelCorners(ModelBase):
    def predict(self, image, step=1):

        border_size = BORDER_SIZE
        white_filled = white_bordered_image(image, border_size)

        stepped_w = int(np.ceil(image.size[0] / step))
        stepped_h = int(np.ceil(image.size[1] / step))
        data = np.zeros((stepped_w * stepped_h,
                         CORNER_FINAL_SIZE,
                         CORNER_FINAL_SIZE,
                         1))

        for ic in tqdm(range(0, image.size[1], step)):
            for jc in range(0, image.size[0], step):
                test_corner = np.array(white_filled.crop((jc - CORNER_RADIUS + border_size,
                                                          ic - CORNER_RADIUS + border_size,
                                                          jc + CORNER_RADIUS + border_size,
                                                          ic + CORNER_RADIUS + border_size))
                                       .resize((CORNER_FINAL_SIZE,
                                                CORNER_FINAL_SIZE))
                                       .getdata()).reshape((1, CORNER_FINAL_SIZE, CORNER_FINAL_SIZE, 1)) / 255.0
                data[ic // step * stepped_w + jc // step] = test_corner

        y_pred = self.model.predict_proba(data, verbose=0)
        res = 1 - y_pred[:, 0] / y_pred.sum(axis=1)
        res = res.reshape((stepped_h, stepped_w))
        # решейпим обратно от сжатого к image.size
        res = (np.array(Image.fromarray((res * 255).astype('uint8')).resize(image.size).getdata())
               .reshape(image.size[::-1]) / 255.0)

        # get list of points from the pixelwise array
        points = raw_list_of_points(res, self.threshold)
        return points


class ModelEdges(ModelBase):
    def predict(self, image, points):
        edges = {ic: [] for ic in range(len(points))}

        border_size = BORDER_SIZE
        white_filled = white_bordered_image(image, border_size)

        corrected_points = [tuple(np.array(p) + [border_size, border_size]) for p in points]
        # predictions = []
        for ic, point_from in enumerate(corrected_points):
            for jc, point_to in enumerate(corrected_points[ic + 1:], start=ic + 1):
                test_corner = np.array(edge_extract(white_filled,
                                                    point_from,
                                                    point_to,
                                                    EDGE_WIDTH)
                                       .resize((EDGE_FINAL_WIDTH,
                                                EDGE_FINAL_LENGTH))
                                       .getdata()).reshape((1, EDGE_FINAL_LENGTH, EDGE_FINAL_WIDTH, 1)) / 255.0
                y_pred = self.model.predict_proba(test_corner, verbose=0)[0]
                # predictions.append((ic, jc, y_pred.copy()))
                y_pred = y_pred[1] / y_pred.sum()
                if y_pred > self.threshold:
                    edges[ic].append(jc)
                    edges[jc].append(ic)

        return edges