import numpy as np
from collections import deque

HARDCODED_HEIGHT = 600
HARDCODED_WIDTH = 800
CLUSTERING_DIST = 7


# def points_to_2d(points):
#     return [(p['x'], p['y']) for p in points]
#
#
# def points_to_dict(points):
#     return [{'x': p[0], 'y': p[1]} for p in points]
#

def dist(point1, point2):
    # return np.sqrt((point1['x'] - point2['x']) ** 2 + (point1['y'] - point2['y']) ** 2)
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


def intersect(edge1, edge2):
    """Определяет точку пересечения двух ребер. Пересечение не обязательно реально
    (если конец одного из ребер почти лежит на втором ребре, но формально ребра не пересекаются)"""
    return (0, 1)


def get_all_intersections(old_points, old_edges):
    """search for every intersection between any of two edges"""
    edges = set()
    for point_from in old_edges:
        for point_to in old_edges[point_from]:
            edges.add((old_points[point_from], old_points[point_to]))
    edges = list(edges)

    while True:
        edge = edges.pop(0)


def modify_edges(edges):
    """если какая-то точка лежит на уже существующем ребре (или очень близка), то
    точка перемещается на ребро; ребро разбивается на 2 новых"""
    points_transform_edges = {}
    for edge1 in edges:
        for edge2 in edges:
            point_intersecting = intersect(edge1, edge2)
            if point_intersecting is None:
                continue
    pass

