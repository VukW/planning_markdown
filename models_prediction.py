from tqdm import tqdm

from app.models import transform_image
from config import DB_FILE_PATH, MODELS_EDGES_MODEL, MODELS_CORNERS_MODEL, MODELS_EDGES_THRESHOLD, \
    MODELS_CORNERS_THRESHOLD, MODELS_CLUSTERING_DIST, MODELS_SAVE_PREDICTION
from data_cleaning.graph import cluster_points, clean_markdown
from data_cleaning.images import clean_image
from models import ModelCorners, ModelEdges
from utils import load_image_from_url, build_new_markdown, json_int_serialize
import numpy as np
import json

if __name__ == "__main__":
    np.random.seed(123)
    # read db file
    with open(DB_FILE_PATH, 'r') as f_to_read_json:
        db_json = json.loads(f_to_read_json.read())

    model_corners = ModelCorners(threshold=MODELS_CORNERS_THRESHOLD )
    model_edges = ModelEdges(threshold=MODELS_EDGES_THRESHOLD)
    model_corners.load(MODELS_CORNERS_MODEL)
    model_edges.load(MODELS_EDGES_MODEL)

    keys = sorted(list(db_json.keys()), key=int)
    for ic, image_id in enumerate(tqdm(keys)):
        # get markdown
        print('start ', image_id)
        section = db_json[image_id]
        image = load_image_from_url(section['url'])

        if 'angle' not in section:
            section['angle'] = 0
        if 'borders' not in section:
            section['borders'] = {
                "bottom_border": image.size[1],
                "left_border": 0,
                "right_border": image.size[1],
                "up_border": 0
            }

        image = transform_image(image, section['angle'], section['borders'])[0]
        image = clean_image(image)
        # predict markdown
        print('predict corners..')
        points = model_corners.predict(image, step=1)
        print('cluster {0} points...'.format(len(points)))
        points = cluster_points(points, clustering_dist=MODELS_CLUSTERING_DIST)[0]
        print('got {0} clustered points, predict edges..'.format(len(points)))
        # print(points)
        edges = model_edges.predict(image, points)
        print('got {0} edges, clean markdown..'.format(len(edges)))
        points, edges = clean_markdown(points, edges, image=image)
        print('got {0} points, {1} edges, build new markdown...'.format(len(points), len(edges)))
        points = [(p[0] - image.size[0] // 2, p[1] - image.size[1] // 2) for p in points]
        new_md = build_new_markdown(points, edges)
        section['markdown'] = new_md

        # save new markdown to file
        if ic % 1 == 0:
            with open(MODELS_SAVE_PREDICTION, 'w') as f:
                print(json.dumps(db_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)

        # if ic == 10:
        #     break
