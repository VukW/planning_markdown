from app.models import transform_image, load_image_from_url
from data_cleaning import *
from config import DB_FILE_PATH
from PIL import Image
import json
from tqdm import tqdm

transformed_images_folder = '../images'


if __name__ == '__main__':
    # read db file
    with open(DB_FILE_PATH, 'r') as f_to_read_json:
        db_json = json.loads(f_to_read_json.read())
    clustered_db_json = {}

    # for every point
    for ic, image_id in tqdm(enumerate(db_json)):
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

        # clean data:
        # for each pair of edges, search for intersection
        get_all_intersections(old_points, old_edges)

        # clean data: cluster points, build new edges
        clustered_points, points_transform_clustering = cluster_points(old_points)
        for point_from in old_edges:
            old_edges[ic] = (points_transform_clustering[edge[0]], points_transform_clustering[edge[1]])
        # transform edges into the dict:
        # {%points_num_from%: [%list of points_num_to%]}
        new_edges = {}

        edges = modify_edges(edges)

        clustered_db_json[image_id]['clustered'] = {'points': clustered_points,
                                                    'edges': edges}

        # image = load_image_from_url(db_json[image_id])
        if ic >= 10:
            break

    with open(DB_FILE_PATH + '.clustered', 'w') as f:
        print(json.dumps(clustered_db_json, indent=4, sort_keys=True), file=f)
