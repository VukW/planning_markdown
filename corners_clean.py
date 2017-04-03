from app.models import transform_image, load_image_from_url
from data_cleaning import *
from config import DB_FILE_PATH
from PIL import Image
import json
from tqdm import tqdm

transformed_images_folder = '../images'


def json_int_serialize(obj):
    if isinstance(obj, int):
        # serial = obj.isoformat()
        # return serial
        return str(obj)
    raise TypeError("Type not serializable")


if __name__ == '__main__':
    np.random.seed(123)
    # read db file
    DB_FILE_PATH = "test2.json"
    with open(DB_FILE_PATH, 'r') as f_to_read_json:
        db_json = json.loads(f_to_read_json.read())
    clustered_db_json = {}

    # for every point
    keys = sorted(list(db_json.keys()))
    # for ic, image_id in tqdm(enumerate(db_json)):
    for ic, image_id in tqdm(enumerate(keys)):
        # get markdown
        markdown = db_json[image_id].get('markdown', {})
        if markdown == {}:
            continue

        # collect points and edges
        # list of points coordinates: [(150, 230), (131, 42), ...]
        old_points = []
        # list of edges by point:{0: [1, 2], 1: [0, 2, 7], 2: [0, 1], ...}
        old_edges = {}

        points_counter = 0
        for md_object in markdown.values():
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
        clustered_db_json[image_id] = {'clustered': {'points': clustered_points,
                                                    'edges': new_edges}}

        # image = load_image_from_url(db_json[image_id])
        if ic >= 10:
            break

    with open(DB_FILE_PATH + '.clustered', 'w') as f:
        print(json.dumps(clustered_db_json, indent=4, sort_keys=True, default=json_int_serialize), file=f)
