import os
import random
from unittest import skip
from piyush_utils.base_test_case import BaseTestCase
from maze_fun.maze import MazeGrid, Cell
from maze_fun.side_winder import SideWinder
from maze_fun.binary_tree import BinaryTree
from maze_fun.hunt_and_kill import HuntAndKill
from maze_fun.recursive_backtracker import RecursiveBackTracker


class MazeTest(BaseTestCase):
    def test_maze_grid_init(self):
        maze = MazeGrid(2, 2)
        self.assertEqual(maze.rows, 2)
        self.assertEqual(maze.rows, 2)
        self.assertEqual(maze.grid[0][0], Cell(0, 0))
        self.assertEqual(maze.grid[0][1], Cell(0, 1))
        self.assertEqual(maze.grid[1][0], Cell(1, 0))
        self.assertEqual(maze.grid[1][1], Cell(1, 1))

        # Testing the configuration
        top_left_cell = maze[0, 0]
        self.assertEqual(top_left_cell.left, None)
        self.assertEqual(top_left_cell.north, None)
        self.assertEqual(top_left_cell.right, Cell(0, 1))
        self.assertEqual(top_left_cell.south, Cell(1, 0))

    def test_get_item(self):
        maze = MazeGrid(2, 2)
        item = maze[0, 0]
        self.assertEqual(item, Cell(0, 0))

    @skip('')
    def test_create_maze_string(self):
        maze = MazeGrid(4, 4)
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'maze1.txt')
        self.assert_file_content_equal_to_string(maze.create_maze_string(), file_path)

    @skip('')
    def test_apply_binary_tree_algorithm(self):
        random.seed(0)
        maze = BinaryTree(4, 4)
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'maze2.txt')
        maze.apply_algorithm()
        self.assert_file_content_equal_to_string(maze.create_maze_string(), file_path)

    @staticmethod
    def create_side_winder_maze() -> MazeGrid:
        random.seed(0)
        maze = SideWinder(4, 4)
        maze.apply_algorithm()
        return maze

    @staticmethod
    def get_maze_test_res(res_name: str) -> str:
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, res_name)
        return file_path

    @skip('')
    def test_apply_side_winder_algorithm(self):
        maze = self.create_side_winder_maze()
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, 'maze3.txt')
        self.assert_file_content_equal_to_string(maze.create_maze_string(), file_path)

    def test_generate_bfs_distance_map(self):
        maze = self.create_side_winder_maze()
        bottom_left = (3, 0)
        correct_map = {
            (3, 0): 0,
            (2, 0): 1,
            (1, 0): 2,
            (1, 1): 3,
            (2, 1): 4,
            (1, 2): 4,
            (0, 1): 4,
            (0, 0): 5,
            (0, 2): 5,
            (1, 3): 5,
            (0, 3): 6,
            (2, 3): 6,
            (2, 2): 7,
            (3, 2): 8,
            (3, 1): 9,
            (3, 3): 9

        }
        output_dict = maze.generate_bfs_distance_map(bottom_left)
        self.assertDictEqual(correct_map, output_dict)

    @skip('')
    def test_create_maze_string_with_distance(self):
        maze = self.create_side_winder_maze()
        bottom_left = (3, 0)
        file_path = self.get_maze_test_res('maze4.txt')
        self.assert_file_content_equal_to_string(maze.create_maze_string_with_distance(bottom_left), file_path)

    @skip('')
    def test_create_maze_string_with_path(self):
        maze = self.create_side_winder_maze()
        bottom_left = (3, 0)
        top_right = (0, 3)
        file_path = self.get_maze_test_res('maze5.txt')
        output_string = maze.create_maze_string_with_path(bottom_left, top_right)
        self.assert_file_content_equal_to_string(output_string, file_path)

    def test_determine_nodes_with_greatest_separation(self):
        maze = self.create_side_winder_maze()
        path_nodes = maze.determine_nodes_with_greatest_separation()
        self.assertEqual(len(path_nodes), 2)
        self.assertIn((3, 1), path_nodes)
        self.assertIn((0, 3), path_nodes)

    @skip('')
    def test_hunt_and_kill_algorithm(self):
        random.seed(1)
        maze = HuntAndKill(4, 4)
        maze.apply_algorithm()
        maze.create_maze_image().save('test.jpg')
        file_path = self.get_maze_test_res('hunt-and-kill.txt')
        output_string = maze.create_maze_string()
        print(output_string)
        self.assert_file_content_equal_to_string(output_string, file_path)

    @skip('')
    def test_recursive_backtracker(self):
        random.seed(1)
        maze = RecursiveBackTracker(4, 4)
        maze.apply_algorithm()
        file_path = self.get_maze_test_res('recursive-backtracker.txt')
        output_string = maze.create_maze_string()
        self.assert_file_content_equal_to_string(output_string, file_path)

    @skip('')
    def test_mask_with_i(self):
        maze = RecursiveBackTracker(6, 5)
        for node in maze.get_border_nodes():
            maze.disable_cell(node[0], node[1])
        for i in [1, 2, 3]:
            maze.enable_cell(0, i)
            maze.disable_cell(i, 1)
            maze.disable_cell(i, 3)

        cell1 = maze[2, 2]
        cell2 = maze[3, 2]

        cell3 = maze[0, 1]
        cell4 = maze[0, 2]
        cell1.link_two_cells(cell2)
        cell3.link_two_cells(cell4)
        test_string = maze.create_maze_string()
        correct_output_file = self.get_maze_test_res('mask-sample.txt')
        print(test_string)
        self.assert_file_content_equal_to_string(test_string, correct_output_file)
