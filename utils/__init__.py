from urllib.request import urlopen
from hashlib import md5
from io import BytesIO
from PIL import Image


def load_image_from_url(url):
    img_io = urlopen(url).read()
    img = Image.open(BytesIO(img_io))
    return img


def image_hash_md5(image):
    output = BytesIO()
    image.save(output, "PNG")
    return md5(output.getvalue()).hexdigest()


def build_new_markdown(clustered_points, new_edges):
    new_markdown = {}
    segment_counter = 0
    for point_from in new_edges:
        for point_to in new_edges[point_from]:
            if point_to < point_from:
                continue
            new_markdown[str(segment_counter)] = {"type": "segment",
                                                  "path": [
                                                      {
                                                          "x": clustered_points[point_from][0],
                                                          "y": clustered_points[point_from][1]
                                                      },
                                                      {
                                                          "x": clustered_points[point_to][0],
                                                          "y": clustered_points[point_to][1]
                                                      }
                                                  ]}
            segment_counter += 1


def json_int_serialize(obj):
    if isinstance(obj, int):
        return str(obj)
    raise TypeError("Type not serializable")
