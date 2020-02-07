from maze_fun.maze import MazeGrid


class HuntAndKill(MazeGrid):
    def apply_algorithm(self):
        frames = [self.create_maze_image()]
        current_cell = self.get_random_cell()
        need_to_visit = self.size() - 1

        while need_to_visit > 0:
            neighbor = current_cell.get_random_unlinked_neighbor()
            if neighbor:
                current_cell.link_two_cells(neighbor)
                current_cell = neighbor
                need_to_visit -= 1
            else:
                # Hunt and kill tme
                for cell in self.yield_each_cell():
                    if not cell.get_links():  # Means that this cell is unvisted
                        hunted_and_killed = False
                        for neighbor in cell.get_neighbors():
                            if neighbor.get_links():
                                current_cell = cell
                                current_cell.link_two_cells(neighbor)
                                need_to_visit -= 1
                                hunted_and_killed = True
                                break
                        if hunted_and_killed:
                            break
                frames.append(self.create_maze_image())
        return frames


if __name__ == '__main__':
    grid = HuntAndKill(20, 20)
    grid.apply_algorithm()
    print(grid.number_of_dead_ends())
