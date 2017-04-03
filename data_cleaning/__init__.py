import numpy as np

HARDCODED_HEIGHT = 600
HARDCODED_WIDTH = 800
CLUSTERING_DIST = 10
EPS_ZERO = 1e-3

# ======
# utils
# ======


def dist(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def list_to_tuple(lst):
    return tuple(int(round(e)) for e in lst)


def edges_dict_to_list(edges_dict):
    edges_list = []
    for point_from in edges_dict:
        for point_to in edges_dict[point_from]:
            if point_to > point_from:
                edges_list.append({'from': point_from, 'to': point_to})
    return edges_list


def edges_list_to_dict(edges_list):
    edges_dict = {}
    for edge in edges_list:
        for point in [edge['from'], edge['to']]:
            if point not in edges_dict:
                edges_dict[point] = []
        edges_dict[edge['from']].append(edge['to'])
        edges_dict[edge['to']].append(edge['from'])
    return edges_dict


def line_from_two_points(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    a = y2 - y1
    b = - (x2 - x1)
    c = y1 * (x2 - x1) - x1 * (y2 - y1)
    return a, b, c


def cluster_points(points):
    """Объединяет рядом лежащие точки в единый кластер"""
    clusters = []  # list of lists
    for point1 in points:
        new_cluster = [point1]
        for ic in range(len(clusters)):
            cluster = clusters[ic]
            for point2 in cluster:
                if dist(point1, point2) < CLUSTERING_DIST:
                    new_cluster += cluster
                    clusters[ic] = []
                    break
        clusters.append(new_cluster)
    clustered_points = []
    points_transform_clustering = {}
    for cluster in clusters:
        if len(cluster) == 0:
            continue
        cluster_mean = list_to_tuple(np.mean(cluster, axis=0))
        clustered_points.append(cluster_mean)
        for point in cluster:
            points_transform_clustering[point] = cluster_mean
    return clustered_points, points_transform_clustering


def transform_edges(old_points, old_edges, new_points, transformation_dict):
    def new_point_pos(old_point):
        return new_points.index(transformation_dict[old_points[old_point]])

    new_edges = {}
    for ic in range(len(new_points)):
        new_edges[ic] = set()
    for point_from in old_edges:
        new_point_from = new_point_pos(point_from)
        for ic in range(len(old_edges[point_from])):
            point_to = old_edges[point_from][ic]
            new_point_to = new_point_pos(point_to)
            if new_point_to != new_point_from:
                new_edges[new_point_from].add(new_point_to)
                new_edges[new_point_to].add(new_point_from)

    for point_from in new_edges:
        new_edges[point_from] = list(new_edges[point_from])
    return new_edges


def dist_point_to_edge(point, edge_start, edge_end):
    x0, y0 = point
    a, b, c = line_from_two_points(edge_start, edge_end)

    if (np.abs(a) < EPS_ZERO) and (np.abs(b) < EPS_ZERO):
        # ребро на самом деле - одна точка
        return dist(edge_start, point), edge_start

    nearest_point = ((b * (b * x0 - a * y0) - a * c) / (a ** 2 + b ** 2),
                     (a * (-b * x0 + a * y0) - b * c) / (a ** 2 + b ** 2))
    dist_ = dist(point, nearest_point)
    if np.dot([nearest_point[0] - edge_start[0],
               nearest_point[1] - edge_start[1]],
              [nearest_point[0] - edge_end[0],
               nearest_point[1] - edge_end[1]]) > 0:
        # nearest point is out of start and end
        dist_ = dist(point, edge_start)
        nearest_point = edge_start
        dist_tmp = dist(point, edge_end)
        if dist_tmp < dist_:
            nearest_point = edge_end
            dist_ = dist_tmp

    return dist_, list_to_tuple(nearest_point)


def link_points_to_nearest_edge(points, edges):
    """for each point it seeks for the nearest edge, then split edge into two parts
    and link point to splitting"""
    # get simple 1d list of all edges
    edges_list = edges_dict_to_list(edges)

    new_points = points.copy()
    edges_splits = [[{'pos': e['to'],
                      'dist_to_start': dist(new_points[e['from']], new_points[e['to']])}] for e in edges_list]
    transformation_dict = {}

    # seek nearest edge for each point
    for ic, point in enumerate(new_points):
        opt_dist = CLUSTERING_DIST
        opt_edge = None
        opt_point = None
        for jc, edge in enumerate(edges_list):
            if ic in [edge['from'], edge['to']]:
                continue
            dist_to_edge, new_point = dist_point_to_edge(point,
                                                         new_points[edge['from']],
                                                         new_points[edge['to']])
            if dist_to_edge <= opt_dist:
                opt_dist = dist_to_edge
                opt_edge = jc
                opt_point = new_point
        if opt_edge is not None:
            transformation_dict[ic] = opt_point
            edges_splits[opt_edge].append({'pos': ic,
                                           'dist_to_start': dist(point,
                                                                 new_points[edges_list[opt_edge]['from']])})

    for edge_splits in edges_splits:
        edge_splits.sort(key=lambda x: x['dist_to_start'])

    # splitting edges..
    new_edges = []
    for edge, edge_splits in zip(edges_list, edges_splits):
        prev_point = edge['from']
        for edge_split in edge_splits:
            new_edges.append({'from': prev_point, 'to': edge_split['pos']})
            prev_point = edge_split['pos']

    # update point positions according to
    for ic in transformation_dict:
        new_points[ic] = transformation_dict[ic]

    return new_points, edges_list_to_dict(new_edges)


def real_intersect(edge1, edge2):
    """находит пересечение двух ребер, если такое есть. Возвращает список из 0..2 точек"""
    line1 = line_from_two_points(edge1[0], edge1[1])
    line2 = line_from_two_points(edge2[0], edge2[1])
    norm1 = np.linalg.norm(line1[:2])
    norm2 = np.linalg.norm(line2[:2])
    cosine_similarity = np.dot(line1[:2], line2[:2]) / (norm1 * norm2)
    if np.abs(cosine_similarity) > 1 - EPS_ZERO:
        # ребра почти параллельны
        norming_sign = np.sign(cosine_similarity)

        dist_between_edges = min([
            dist_point_to_edge(edge1[0], edge2[0], edge2[1])[0],
            dist_point_to_edge(edge1[1], edge2[0], edge2[1])[0],
            dist_point_to_edge(edge2[0], edge1[0], edge1[1])[0],
            dist_point_to_edge(edge2[1], edge1[0], edge1[1])[0]
        ])
        if dist_between_edges > CLUSTERING_DIST:
            # ребра параллельны, но на разных линиях
            return []
        # ребра лежат на одной линии
        four_points = [edge1[0], edge1[1], edge2[0], edge2[1]]
        four_points.sort()
        return four_points[1:3]

    full_mat = np.array([line1, line2])
    det = np.linalg.det(full_mat[:, [0, 1]])
    x = - np.linalg.det(full_mat[:, [2, 1]]) / det
    y = - np.linalg.det(full_mat[:, [0, 2]]) / det
    intersection_point = list_to_tuple([x, y])

    # проверим, что точка на самом деле лежит на обоих ребрах
    if ((np.dot(np.array(intersection_point) - np.array(edge1[0]),
                np.array(intersection_point) - np.array(edge1[1])) <= 0)
        and
            (np.dot(np.array(intersection_point) - np.array(edge2[0]),
                    np.array(intersection_point) - np.array(edge2[1])) <= 0)):
        return [intersection_point]
    else:
        return []


def add_all_intersections(old_points, old_edges):
    """search for every intersection between any of two edges and split these edges accordingly"""
    new_points = old_points.copy()
    edges = edges_dict_to_list(old_edges)
    edges_splits = [[] for _ in range(len(edges))]

    for ic, edge1 in enumerate(edges):
        for jc, edge2 in enumerate(edges[ic + 1:]):
            intersection_points = real_intersect([new_points[edge1['from']],
                                                  new_points[edge1['to']]],
                                                 [new_points[edge2['from']],
                                                  new_points[edge2['to']]])
            if len(intersection_points) == 0:
                # пересечений нет
                continue
            else:
                # точки пересечения (1 либо 2)
                # две может быть, если оба ребра лежат на одной линии и пересекаются
                for intersection_point in intersection_points:
                    if intersection_point not in new_points:
                        intersection_point_pos = len(new_points)
                        new_points.append(intersection_point)
                    else:
                        intersection_point_pos = new_points.index(intersection_point)

                    edges_splits[ic].append({'pos': intersection_point_pos,
                                             'dist_to_start': dist(intersection_point,
                                                                   new_points[edge1['from']])})
                    edges_splits[ic + jc + 1].append({'pos': intersection_point_pos,
                                                      'dist_to_start': dist(intersection_point,
                                                                            new_points[edge2['from']])})
        edges_splits[ic].append({'pos': edge1['to'],
                                 'dist_to_start': dist(new_points[edge1['to']],
                                                       new_points[edge1['from']])})
        edges_splits[ic].sort(key=lambda x: x['dist_to_start'])

    # splitting edges..
    new_edges = []
    for edge, edge_splits in zip(edges, edges_splits):
        prev_point = edge['from']
        for edge_split in edge_splits:
            new_edges.append({'from': prev_point, 'to': edge_split['pos']})
            prev_point = edge_split['pos']

    return new_points, edges_list_to_dict(new_edges)
