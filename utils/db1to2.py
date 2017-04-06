"""converts db from format 1.0 into format 2.0
1.0: points in range (0, 800) x (0, 600)
2.0: points in range(-w/2; +w/2) x (-h/2; +h/2)
"""

import argparse
import json
# from os.path import isfile
# from shutil import copyfile

parser = argparse.ArgumentParser(description="convert db (format 1.0) to format 2.0")
parser.add_argument('-f', '--fromfile', type=str, required=True, help='file to convert from')
parser.add_argument('-t', '--tofile', type=str, required=True, help='file to save to')

args = parser.parse_args()

from_file = args.fromfile
to_file = args.tofile

# bak_file = None
# for ic in range(1000):
#     bak_file = from_file + ".bak"
#     if not isfile(bak_file):
#         break
#
# if isfile(bak_file):
#     raise ValueError('backup files for {0} already exist. '
#                      'Delete some and run this script one more time'.format(from_file))

with open(from_file, 'r') as f:
    db = json.loads(f.read())

for image_id in db:
    image_obj = db[image_id]
    md = image_obj.get('markdown', {})
    if md == {}:
        continue
    real_width = image_obj['borders']['right_border'] - image_obj['borders']['left_border']
    real_height = image_obj['borders']['bottom_border'] - image_obj['borders']['up_border']
    for obj in md:
        new_path = []
        for point in md[obj]['path']:
            point['x'] = int((point['x'] - 400) * real_width / 800)
            point['y'] = int((point['y'] - 300) * real_height / 600)

with open(to_file, 'w') as f:
    print(json.dumps(db, indent=4, sort_keys=True), file=f)
