import json
import numpy as np
from tqdm import tqdm

from config import DB_FILE_PATH, CLEAN_SAVE_CLUSTERED_GRAPH, CLEAN_SAVE_CLUSTERED_GRAPH_FOR_WEB_SERVICE, CLEAN_SAVE_CORNERS_DF, \
    CLEAN_SAVE_EDGES_DF
from data_cleaning.graph import clean_markdown
from app.models import load_image_from_url, transform_image
from data_cleaning.images import save_corners, save_image, transform_corners, DataFrameForCornersClassifier, clean_image, \
    DataFrameForEdgesClassifier
from utils import build_new_markdown, json_int_serialize

if __name__ == '__main__':
    np.random.seed(123)
    # read db file
    with open(DB_FILE_PATH, 'r') as f_to_read_json:
        db_json = json.loads(f_to_read_json.read())

    # {image_id: {
    #   "points": [(x1, y1), .., (xk, yk)]
    #   "edges":
    # }}
    clustered_only_json = {}
    web_service_new_db_json = {}
    classified_corners_df = DataFrameForCornersClassifier()
    classified_edges_df = DataFrameForEdgesClassifier()
    # for every point
    keys = sorted(list(db_json.keys()))
    progress_bar = tqdm(total=300)
    for ic, image_id in enumerate(keys):
        # get markdown
        markdown = db_json[image_id].get('markdown', {})
        if markdown == {}:
            continue

        # print(image_id)

        # collect points and edges
        # list of points coordinates: [(150, 230), (131, 42), ...]
        old_points = []
        # list of edges by point:{0: [1, 2], 1: [0, 2, 7], 2: [0, 1], ...}
        old_edges = {}

        points_counter = 0
        for md_index in sorted(markdown.keys()):
            md_object = markdown[md_index]
            prev_point = None
            for point in md_object['path']:
                point_tpl = (point['x'], point['y'])
                old_points.append(point_tpl)
                if prev_point is not None:
                    edges_by_point = old_edges.get(prev_point, [])
                    old_edges[prev_point] = edges_by_point + [points_counter]
                    old_edges[points_counter] = [prev_point]
                prev_point = points_counter
                points_counter += 1

        # clean the data
        clustered_points, new_edges = clean_markdown(old_points, old_edges)

        # save
        clustered_only_json[image_id] = {'clustered': {'points': clustered_points,
                                                       'edges': new_edges}}
        # save as db-markdown
        web_service_new_db_json[image_id] = db_json[image_id]

        new_markdown = build_new_markdown(clustered_points, new_edges)

        web_service_new_db_json[image_id]['markdown'] = new_markdown

        # load image, transform, save corners
        image = load_image_from_url(db_json[image_id]['url'])
        image = transform_image(image, db_json[image_id]['angle'], db_json[image_id]['borders'])[0]
        image = clean_image(image)
        save_image(image, image_id)
        real_size = image.size  # w, h
        resized_clustered_points = transform_corners(clustered_points, db_json[image_id]['borders'], real_size)
        save_corners(image, image_id, resized_clustered_points)
        classified_corners_df.append(image, image_id, resized_clustered_points, new_edges)
        classified_edges_df.append(image, image_id, resized_clustered_points, new_edges)
        progress_bar.update(1)

    # saving cleaned jsons
    # clustered format
    with open(CLEAN_SAVE_CLUSTERED_GRAPH, 'w') as f:
        print(json.dumps(clustered_only_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)

    # save clean graph as db-markdown format (for web service)
    with open(CLEAN_SAVE_CLUSTERED_GRAPH_FOR_WEB_SERVICE, 'w') as f:
        print(json.dumps(web_service_new_db_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)

    # classifier
    classified_corners_df.save(CLEAN_SAVE_CORNERS_DF)
    classified_edges_df.save(CLEAN_SAVE_EDGES_DF)
