"""converts db from format 2.0 into format 3.0
3.0: for each picture hash is added
"""

import argparse
import json
from tqdm import tqdm
from utils import load_image_from_url, image_hash_md5

parser = argparse.ArgumentParser(description="convert db (format 2.0) to format 3.0 (adding hash for every picture")
parser.add_argument('-f', '--fromfile', type=str, required=True, help='file to convert from')
parser.add_argument('-t', '--tofile', type=str, required=True, help='file to save to')

args = parser.parse_args()

from_file = args.fromfile
to_file = args.tofile

with open(from_file, 'r') as f:
    db = json.loads(f.read())

for image_id in tqdm(db):
    image_obj = db[image_id]
    md = image_obj.get('markdown', {})
    if md == {}:
        continue
    image = load_image_from_url(image_obj['url'])
    image_obj['hash_md5'] = image_hash_md5(image)

with open(to_file, 'w') as f:
    print(json.dumps(db, indent=4, sort_keys=True), file=f)
