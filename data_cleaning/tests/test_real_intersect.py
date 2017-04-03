from unittest import TestCase
from data_cleaning import real_intersect, dist_point_to_edge


class TestReal_intersect(TestCase):

    def test_interaction_parallel_1(self):
        edge1 = [(78, 201), (718, 201)]
        edge2 = [(78, 497), (434, 495)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_2(self):
        edge1 = [(78, 201), (718, 201)]
        edge2 = [(78, 497), (434, 400)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_3(self):
        edge1 = [(78, 201), (718, 201)]
        edge2 = [(78, 497), (434, 497)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_4(self):
        edge1 = [(78, 201), (718, 201)]
        edge2 = [(78, 497), (434, 495)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_5(self):
        # лежат близко друг к другу: начинаются в одной точке
        edge1 = [(78, 201), (718, 201)]
        edge2 = [(78, 205), (434, 207)]
        self.assertEqual(real_intersect(edge1, edge2), edge2)

    def test_interaction_parallel_6(self):
        # лежат близко друг к другу: первая поглощает вторую
        edge1 = [(40, 201), (718, 201)]
        edge2 = [(78, 205), (434, 207)]
        self.assertEqual(real_intersect(edge1, edge2), edge2)

    def test_interaction_parallel_7(self):
        # лежат близко друг к другу: общий кусок
        edge1 = [(150, 201), (718, 201)]
        edge2 = [(78, 205), (434, 207)]
        self.assertEqual(real_intersect(edge1, edge2), [(150, 201), (434, 207)])

    def test_interaction_parallel_8(self):
        # лежат близко друг к другу, пересекаются
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(100, 102), (300, 98)]
        self.assertEqual(real_intersect(edge1, edge2), [(100, 102), (300, 98)])

    def test_interaction_parallel_9(self):
        # параллельны, пересекаются концом
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(50, 100), (100, 100)]
        self.assertEqual(real_intersect(edge1, edge2), [(100, 100), (100, 100)])

    def test_interaction_parallel_10(self):
        # не параллельны, пересекаются
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(50, 50), (350, 150)]
        self.assertEqual(real_intersect(edge1, edge2), [(200, 100)])

    def test_interaction_parallel_11(self):
        # не параллельны, не пересекаются
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(50, 150), (350, 250)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_12(self):
        # перпендикулярны, пересекаются концом
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(100, 50), (100, 100)]
        self.assertEqual(real_intersect(edge1, edge2), [(100, 100)])

    def test_interaction_parallel_13(self):
        # перпендикулярны, почти пересекатся
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(100, 50), (100, 99)]
        self.assertEqual(real_intersect(edge1, edge2), [])

    def test_interaction_parallel_14(self):
        # перпендикулярны, пересекаются
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(100, 50), (100, 150)]
        self.assertEqual(real_intersect(edge1, edge2), [(100, 100)])

    def test_interaction_parallel_15(self):
        # перпендикулярны, пересекаются
        edge1 = [(100, 100), (500, 100)]
        edge2 = [(150, 50), (150, 150)]
        self.assertEqual(real_intersect(edge1, edge2), [(150, 100)])
