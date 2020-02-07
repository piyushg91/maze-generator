from piyush_utils.base_test_case import BaseTestCase
from maze_fun.maze import MazeGrid
from maze_fun.cell import Cell



class CellTest(BaseTestCase):
    def test_get_unlinked_neighbors(self):
        maze = MazeGrid(4, 4)
        bottom_left_cell = maze[3, 0]
        n = bottom_left_cell.get_unlinked_neighbors()
        self.assertEqual(len(n), 2)
        self.assertEqual(n[0].pos, (2, 0))
        self.assertEqual(n[1].pos, (3, 1))

    def test_get_unlinked_neighbors_none(self):
        maze = MazeGrid(4, 4)
        bottom_left_cell = maze[3, 0]
        top, right = maze[2, 0], maze[3, 1]
        bottom_left_cell.link_two_cells(top)
        bottom_left_cell.link_two_cells(right)
        n = bottom_left_cell.get_unlinked_neighbors()
        self.assertEqual(n, [])
