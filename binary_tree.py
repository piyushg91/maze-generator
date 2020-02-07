from PIL import Image
from random import choice
from maze_fun.maze import MazeGrid


class BinaryTree(MazeGrid):
    def apply_algorithm(self) -> Image:
        frames = [self.create_maze_image()]
        for row in self.each_row():
            for col in self.each_col():
                cell = self[row, col]
                neighbors = []
                if cell.north:
                    neighbors.append(cell.north)
                if cell.right:
                    neighbors.append(cell.right)

                # Don't run the random function if there's only one for unit testing pursoes
                if len(neighbors) == 1:
                    cell.link_two_cells(neighbors[0])
                elif len(neighbors) == 0:
                    continue
                else:
                    n = choice(neighbors)
                    cell.link_two_cells(n)
                frames.append(self.create_maze_image())
        return frames


if __name__ == '__main__':
    grid = BinaryTree(10, 10)
    frames = grid.create_maze_path_frames()
    MazeGrid.create_gif_from_frames(frames, 'output.gif')
