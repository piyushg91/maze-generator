import random
from PIL import Image
from typing import List
from maze_fun.maze import MazeGrid
from maze_fun.cell import Cell


class Wilson(MazeGrid):
    def apply_algorithm(self) -> Image:
        frames = [self.create_maze_image()]
        unvisted = set()
        for row in self.each_row():
            for col in self.each_col():
                unvisted.add(self[row, col])
        first = random.sample(unvisted, 1)[0]
        unvisted.remove(first)
        while unvisted:
            print('Length of unvisited is ' + str(len(unvisted)))
            cell = random.sample(unvisted, 1)[0] # type: Cell
            path = [cell]  # type: List[Cell]

            while cell in unvisted:
                random_neighbor = cell.get_random_neighbor()
                if random_neighbor in path:
                    index = path.index(random_neighbor)
                    path = path[0:index]
                path.append(random_neighbor)
                cell = random_neighbor

            for i, p in enumerate(path[0:-1]):
                p.link_two_cells(path[i+1])
                unvisted.remove(p)
            frames.append(self.create_maze_image())

        return frames


if __name__ == '__main__':
    random.seed(1)
    w = Wilson(10, 10)
    frames = w.create_maze_path_frames()
    w.create_gif_from_frames(frames, 'wilson.gif')
