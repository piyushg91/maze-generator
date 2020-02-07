from maze_fun.maze import MazeGrid


class RecursiveBackTracker(MazeGrid):

    def apply_algorithm(self, video_output_path: str=None):
        video_writer = None
        if video_output_path:
            starting_image = self.create_maze_image()
            video_writer = self.get_video_writer(starting_image, video_output_path)
            self.write_frame_to_video_writer(video_writer, starting_image)
        cell = self.get_random_cell()
        stack = [cell]
        need_to_vist = self.enabled_size - 1
        num_of_frames_left = 6

        while need_to_vist > 0:
            rand_neighbor = cell.get_random_unlinked_neighbor()
            if rand_neighbor:
                cell.link_two_cells(rand_neighbor)
                cell = rand_neighbor
                stack.append(cell)
                need_to_vist -= 1
                if video_writer and num_of_frames_left == 0:
                    frame = self.create_maze_image()
                    self.write_frame_to_video_writer(video_writer, frame)
                    num_of_frames_left = 6
                else:
                    num_of_frames_left -= 1
            else:
                stack.pop(-1)
                cell = stack[-1] # set it to the last
        return video_writer


if __name__ == '__main__':
    maze = RecursiveBackTracker(20, 20)
    maze.apply_algorithm(video_output_path='rec.mp4')
