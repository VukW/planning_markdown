from unittest import TestCase
from data_cleaning import dist_point_to_edge


class TestDist_point_to_edge_horizontal(TestCase):
    def always_fail(self):
        self.fail()

    def setUp(self):
        self.edge_start = (100, 100)
        self.edge_end = (100, 500)

    def horizontal_point_start_on_line(self):
        point = self.edge_start
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def horizontal_point_inside_on_line(self):
        point = (100, 200)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def horizontal_point_outside_on_line(self):
        point = (100, 600)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 100, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)

    def horizontal_point_start_out_line(self):
        point = (50, 100)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, self.edge_start)

    def horizontal_point_inside_out_line(self):
        point = (150, 150)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, (150, 100))

    def horizontal_point_outide_out_line(self):
        point = (140, 530)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)


class TestDist_point_to_edge_vertical(TestCase):
    def setUp(self):
        self.edge_start = (100, 100)
        self.edge_end = (500, 100)

    def vertical_point_start_on_line(self):
        point = self.edge_start
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def vertical_point_inside_on_line(self):
        point = (200, 100)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def vertical_point_outside_on_line(self):
        point = (600, 100)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 100, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)

    def vertical_point_start_out_line(self):
        point = (100, 50)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, self.edge_start)

    def vertical_point_inside_out_line(self):
        point = (150, 150)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, (100, 150))

    def vertical_point_outide_out_line(self):
        point = (530, 140)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 50, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)


class TestDist_point_to_edge_inclined(TestCase):
    def setUp(self):
        self.edge_start = (100, 100)
        self.edge_end = (200, 300)

    def inclined_point_start_on_line(self):
        point = self.edge_start
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def inclined_point_inside_on_line(self):
        point = (150, 200)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 0, delta=1e-5)
        self.assertEqual(new_point, point)

    def inclined_point_outside_on_line(self):
        point = (300, 500)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 223.60679774997897, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)

    def inclined_point_start_out_line(self):
        point = (100, 350)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 111.80339887498948, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)

    def inclined_point_inside_out_line(self):
        point = (50, 250)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 111.80339887498948, delta=1e-5)
        self.assertEqual(new_point, (150, 200))

    def inclined_point_outide_out_line(self):
        point = (100, 500)
        dist_, new_point = dist_point_to_edge(point, self.edge_start, self.edge_end)
        self.assertAlmostEqual(dist_, 223.60679774997897, delta=1e-5)
        self.assertEqual(new_point, self.edge_end)