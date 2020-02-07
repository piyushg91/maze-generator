from PIL import Image
from random import choice
from maze_fun.maze import MazeGrid


class SideWinder(MazeGrid):
    def apply_algorithm(self) -> Image :
        frames = [self.create_maze_image()]
        for row in self.each_row():
            stack = []
            at_north_boundary = row == 0
            for col in self.each_col():
                cell = self[row, col]
                stack.append(cell)
                coin_flip = self.coin_flip()
                at_right_boundary = col == self.cols-1

                should_close_out = False
                if at_right_boundary:
                    should_close_out = True
                elif not at_north_boundary and coin_flip == 'heads':
                    should_close_out = True
                if should_close_out:
                    random_cell = choice(stack)
                    if random_cell.north:
                        random_cell.link_two_cells(random_cell.north)
                        frames.append(self.create_maze_image())
                    stack.clear()
                else:
                    cell.link_two_cells(cell.right)
                    frames.append(self.create_maze_image())
        return frames


if __name__ == '__main__':
    grid = SideWinder(10, 10)
    frames = grid.create_maze_path_frames()
    MazeGrid.create_gif_from_frames(frames, 'output.gif')
