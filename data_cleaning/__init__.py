import numpy as np

HARDCODED_HEIGHT = 600
HARDCODED_WIDTH = 800
CLUSTERING_DIST = 7


def dist(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def cluster_points(points):
    """Объединяет рядом лежащие точки в единый кластер"""
    # points = points_to_2d(points)
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
        cluster_mean = np.mean(cluster, axis=0)
        clustered_points.append(cluster_mean)
        for point in cluster:
            points_transform_clustering[point] = cluster_mean
    return clustered_points, points_transform_clustering


def transform_edges(old_points, old_edges, new_points, transformation_dict):

    def new_point_pos(old_point):
        return new_points.index(transformation_dict[old_points[old_point]])

    new_edges = {}
    for point_from in old_edges:
        new_point_from = new_point_pos(point_from)
        if new_point_from not in new_edges:
            new_edges[new_point_from] = set()
        for ic in range(len(old_edges[point_from])):
            point_to = old_edges[point_from][ic]
            new_point_to = new_point_pos(point_to)
            if new_point_to != new_point_from:
                new_edges[new_point_from].add(new_point_to)

    for point_from in new_edges:
        new_edges[point_from] = list(new_edges[point_from])
    return new_edges

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
        edges_dict[edge['from']] += edge['to']
        edges_dict[edge['to']] += edge['from']
    return edges_dict

def dist_point_to_edge(point, edge_start, edge_end):
    # TODO: not implemented
    return 0


def link_points_to_nearest_edge(points, edges):
    """for each point it seeks for the nearest edge, then split edge into two parts
    and link point to splitting"""
    # get simple 1d list of all edges
    edges_list = edges_dict_to_list(edges)
    # seek nearest edge for each point
    transformation_dict = {}
    for point in points:
        opt_dist = 1000
        opt_edge = None
        for ic, edge in enumerate(edges_list):
            dist_to_edge = dist_point_to_edge(points[point], points[edge['from']], points[edge['to']])
            if dist_to_edge < opt_dist:
                opt_dist = dist_to_edge
                opt_edge = ic
        if opt_edge is not None:
            transformation_dict[point] = opt_edge

    # transform edges according to built dict
    for point in transformation_dict:
        edge = transformation_dict[point]
        if

# def intersect(edge1, edge2):
#     """Определяет точку пересечения двух ребер. Пересечение не обязательно реально
#     (если конец одного из ребер почти лежит на втором ребре, но формально ребра не пересекаются)"""
#     return (0, 1)

def real_intersect(edge1, edge2):
    #TODO: not implemented
    return (0, 1)

def add_all_intersections(old_points, old_edges):
    """search for every intersection between any of two edges and split these edges accordingly"""
    new_points = old_points.copy()
    edges = edges_dict_to_list(old_edges)
    edges_splits = [[] for _ in range(len(edges))]

    for ic, edge1 in enumerate(edges):
        for jc, edge2 in enumerate(edges[ic:]):
            intersection_point = real_intersect(edge1, edge2)
            if intersection_point not in new_points:
                intersection_point_pos = len(new_points)
                new_points.append(intersection_point)
            else:
                intersection_point_pos = new_points.index(intersection_point)

            if intersection_point is not None:
                edges_splits[ic].append({'pos': intersection_point_pos,
                                         'dist_to_start': dist(intersection_point, edge1['from'])})
                edges_splits[jc].append({'pos': intersection_point_pos,
                                         'dist_to_start': dist(intersection_point, edge1['to'])})
        edges_splits[ic].append({'pos': edge1['to'],
                                 'dist_to_start': dist(edge1['to'], edge1['from'])})
        edges_splits[ic].sort(key=lambda x: x['dist_to_start'])

    # splitting edges..
    new_edges = []
    for edge, edge_splits in zip(edges, edges_splits):
        prev_point = edge['from']
        for edge_split in edge_splits:
            new_edges.append({'from': prev_point, 'to': edge_split['pos']})

    return new_points, edges_list_to_dict(new_edges)

# def modify_edges(edges):
#     """если какая-то точка лежит на уже существующем ребре (или очень близка), то
#     точка перемещается на ребро; ребро разбивается на 2 новых"""
#     points_transform_edges = {}
#     for edge1 in edges:
#         for edge2 in edges:
#             point_intersecting = intersect(edge1, edge2)
#             if point_intersecting is None:
#                 continue
#     pass
#
