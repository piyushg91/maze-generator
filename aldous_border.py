from maze_fun.maze import MazeGrid


class AldousBorder(MazeGrid):
    def apply_algorithm(self):
        frames = [self.create_maze_image()]
        current_cell = self.get_random_cell()
        need_to_visit = self.size() - 1

        while need_to_visit > 0:
            neighbor = current_cell.get_random_neighbor()
            if not neighbor.get_links():
                current_cell.link_two_cells(neighbor)
                need_to_visit -= 1
                frames.append(self.create_maze_image())
            current_cell = neighbor
        return frames


if __name__ == '__main__':
    grid = AldousBorder(10, 10)
    frames = grid.apply_algorithm()
    grid.create_gif_from_frames(frames, 'happy.gif')