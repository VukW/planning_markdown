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
