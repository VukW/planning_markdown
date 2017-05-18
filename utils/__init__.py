from urllib.request import urlopen
from hashlib import md5
from io import BytesIO
from PIL import Image
from PIL import ImageDraw


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
    return new_markdown


def json_int_serialize(obj):
    if isinstance(obj, int):
        return str(obj)
    raise TypeError("Type not serializable")


def draw_points(image, points, edges=None):
    image = image.copy().convert("RGB")
    canvas = ImageDraw.Draw(image)
    if edges is not None:
        for ic in edges:
            for jc in edges[ic]:
                if jc <= ic:
                    continue
                canvas.line([tuple(points[ic]), tuple(points[jc])], fill=(0, 255, 128), width=5)

    for p in points:
        canvas.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5),
                       fill=(255, 128, 10))
    del canvas
    return image
