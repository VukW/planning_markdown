import json
import numpy as np
from PIL import Image
from tqdm import tqdm

from config import DB_FILE_PATH
from data_cleaning.graph import cluster_points, transform_edges, link_points_to_nearest_edge, add_all_intersections
from app.models import load_image_from_url, transform_image
from data_cleaning.images import  save_corners, save_image, transform_corners, DataFrameForClassifier


def json_int_serialize(obj):
    if isinstance(obj, int):
        return str(obj)
    raise TypeError("Type not serializable")


if __name__ == '__main__':
    np.random.seed(123)
    # read db file
    with open(DB_FILE_PATH, 'r') as f_to_read_json:
        db_json = json.loads(f_to_read_json.read())
    clustered_only_json = {}
    web_service_new_db_json = {}
    classified_df = DataFrameForClassifier()

    # for every point
    keys = sorted(list(db_json.keys()))
    # for ic, image_id in tqdm(enumerate(db_json)):
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

        # =======================
        # clean the data:
        # 1. add all intersections between edges
        new_points, new_edges = add_all_intersections(old_points, old_edges)
        # 2. cluster points
        # 3. transform edges with transformation dict
        clustered_points, transformation_dict = cluster_points(new_points)
        new_edges = transform_edges(new_points, new_edges, clustered_points, transformation_dict)
        # 4. for every point we seek for the nearest edge and link it here
        new_points, new_edges = link_points_to_nearest_edge(clustered_points, new_edges)
        # 5, 6. repeat clustering
        clustered_points, transformation_dict = cluster_points(new_points)
        new_edges = transform_edges(new_points, new_edges, clustered_points, transformation_dict)
        # cleaning finished
        # =======================

        # save
        clustered_only_json[image_id] = {'clustered': {'points': clustered_points,
                                                       'edges': new_edges}}
        # save as db-markdown
        web_service_new_db_json[image_id] = db_json[image_id]
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

        web_service_new_db_json[image_id]['markdown'] = new_markdown

        # load image, transform, save corners
        image = load_image_from_url(db_json[image_id]['url'])
        image = transform_image(image, db_json[image_id]['angle'], db_json[image_id]['borders'])[0]
        save_image(image, image_id)
        real_size = image.size # w, h
        resized_clustered_points = transform_corners(clustered_points, db_json[image_id]['borders'], real_size)
        save_corners(image, image_id, resized_clustered_points)
        classified_df.append(image, image_id, resized_clustered_points)
        progress_bar.update(1)

    # saving cleaned jsons
    # clustered format
    with open(DB_FILE_PATH + '.clustered', 'w') as f:
        print(json.dumps(clustered_only_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)

    # save clean graph as db-markdown format (for web service)
    with open(DB_FILE_PATH + '-cleaned.json', 'w') as f:
        print(json.dumps(web_service_new_db_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)

    # classifier
    classified_df.save(DB_FILE_PATH + '-dataframe.csv')
