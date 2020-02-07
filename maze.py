import os
import cv2
import numpy as np
from typing import Optional, List, Tuple, Dict
from random import randint, choice
from maze_fun.cell import Cell
from PIL import Image, ImageDraw, ImageFont


class MazeGrid(object):
    fill_white = (255, 255, 255)
    fill_black = (0, 0, 0)
    fill_blue = (0, 0, 255)
    default_cell_size = 100
    maze_wall_width = 5

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.grid = self.init_starting_grid()
        self.configure_cells()
        self.enabled_map = self.create_enabled_map()
        self.enabled_size = self.size()

    def create_enabled_map(self) -> Dict[Tuple, bool]:
        output = {}
        for cell in self.yield_each_cell():
            output[cell.pos] = True
        return output

    def disable_cell(self, row: int, col: int):
        cell = self[row, col]
        if cell is None:
            raise Exception('Could not find a cell mapped at  {0} and {1}'.format(row, col))
        if cell.enabled:
            cell.disable_cell()
            self.enabled_size -= 1
        else:
            raise Exception('Trying to disable a cell that is already disabled')

    def enable_cell(self, row: int, col: int):
        cell = self[row, col]
        if cell is None:
            raise Exception('Could not find a cell mapped at  {0} and {1}'.format(row, col))
        if not cell.enabled:
            cell.enable_cell()
            self.enabled_size += 1
        else:
            raise Exception('Trying to enable a cell that is already enabled')

    def init_starting_grid(self):
        grid = []
        for row_num in range(self.rows):
            row = []
            for col_num in range(self.cols):
                new_cell = Cell(row_num, col_num)
                row.append(new_cell)
            grid.append(row)
        return grid

    def create_maze_string(self, distance_map: Dict=None):
        maze_list = []
        bottom_border = ''
        space_4 = ' ' * 4
        for row in self.each_row():
            upper_border = ''
            corrider = ''
            for col in self.each_col():
                cell = self[row, col]
                if cell.enabled:
                    if cell.north and cell.north.enabled and cell.is_linked(cell.north):
                        # Draw horizontal wall
                        upper_border += '+   '
                    else:
                        upper_border += '+---'
                    if cell.left and cell.left.enabled and cell.is_linked(cell.left):
                        corrider += space_4
                    else:
                        corrider += '|   '

                    if not cell.right:
                        corrider += '|'
                        # upper_border += '+'
                else:
                    if cell.left and cell.left.enabled:
                        corrider += '|  '
                        if upper_border:
                            upper_border += '+'
                    else:
                        corrider += '    '
                    if cell.north and cell.north.enabled:
                        upper_border += '+---'
                    else:
                        upper_border += space_4


            maze_list.append(upper_border)
            maze_list.append(corrider)
        for i in range(self.cols):
            cell = self[self.rows - 1, i]
            if cell.enabled:
                bottom_border += '+---'
            else:
                bottom_border += space_4
        maze_list.append(bottom_border)
        return '\n'.join(maze_list)

    def create_maze_string_with_distance(self, starting_node: Tuple[int, int]):
        """
        :param starting_node:
        :return:
        """
        distance_map = self.generate_bfs_distance_map(starting_node)
        return self.create_maze_string(distance_map)

    def get_stripped_dist_map_between_two_nodes(self, starting_node: Tuple[int, int],
                                                ending_node: Tuple[int, int]) -> Dict[Tuple[int, int], int]:
        distance_map = self.generate_bfs_distance_map(starting_node)
        stripped_distance_map = {}
        current_node = ending_node
        current_distance_to_starting_node = distance_map[current_node]
        stripped_distance_map[ending_node] = distance_map[ending_node]
        while current_distance_to_starting_node > 0:
            cell = self[current_node]
            current_distance_to_starting_node = distance_map[current_node]
            for n in cell.get_links():
                if distance_map[n.pos] == current_distance_to_starting_node - 1:
                    current_node = n.pos
                    stripped_distance_map[n.pos] = distance_map[n.pos]
                    break
        return stripped_distance_map

    def create_maze_string_with_path(self, starting_node: Tuple[int, int], ending_node: Tuple[int, int]):
        stripped_distance_map = self.get_stripped_dist_map_between_two_nodes(starting_node, ending_node)
        return self.create_maze_string(stripped_distance_map)

    def get_base_image_size(self):
        return self.default_cell_size*self.cols + self.maze_wall_width, \
               self.default_cell_size*self.rows + self.maze_wall_width

    def create_maze_path_frames(self):
        video_writer = self.apply_algorithm('test.mp4')
        cell_size = self.default_cell_size
        path_margin = 30
        image_size = self.get_base_image_size()
        starting_node, ending_node = self.determine_nodes_with_greatest_separation()
        frame_with_start_and_end_points = self.create_maze_image(None, starting_node, ending_node, False)
        self.place_frame_on_background_and_write_to_video_file(frame_with_start_and_end_points, video_writer,
                                                               image_size)
        stripped_dist_map = self.get_stripped_dist_map_between_two_nodes(starting_node, ending_node)
        last_frame = frame_with_start_and_end_points
        for node, dist in sorted(stripped_dist_map.items(), key=lambda kv: kv[1]):
            row, col = node
            drawer = ImageDraw.Draw(last_frame)
            rectangle_loc = [col*cell_size + path_margin,
                             row*cell_size + path_margin,
                             (col+1)*cell_size - path_margin,
                             (row+1)*cell_size - path_margin]
            drawer.rectangle(rectangle_loc, fill=self.fill_blue)

            self.place_frame_on_background_and_write_to_video_file(last_frame, video_writer, image_size)
        for i in range(15):
            self.place_frame_on_background_and_write_to_video_file(last_frame, video_writer, image_size)

    def place_frame_on_background_and_write_to_video_file(self, frame: Image, writer: cv2.VideoWriter, image_size):
        copied_frame = frame.copy()
        frame_with_bg = self.place_maze_on_background(copied_frame, image_size)
        self.write_frame_to_video_writer(writer, frame_with_bg)

    def create_maze_image_with_path(self, starting_node: Tuple[int, int], ending_node: Tuple[int, int],
                                    output_file_path: str):
        image = self.create_maze_image(None, starting_node, ending_node)
        image.save(output_file_path)

    @staticmethod
    def convert_num_to_maze_distance(num: int) -> str:
        if num > 9:
            return chr(87 + num)
        return str(num)

    def create_maze_image(self, distance_map: Dict=None, starting_node: Tuple[int, int]=None,
                          ending_node: Tuple[int, int]=None, place_on_background: bool=True) -> Image:
        cell_size = self.default_cell_size
        maze_width = 5
        image_size = self.get_base_image_size()
        image = Image.new('RGB', image_size, color=self.fill_white)
        drawer = ImageDraw.Draw(image)
        all_possible_line_segments = self.get_set_of_all_possible_line_segments()
        for row in self.each_row():
            for col in self.each_col():
                cell = self[row, col]
                if not cell.enabled:
                    continue
                if cell.right and cell.is_linked(cell.right):
                    x = col + 1
                    x1, y1 = x, row
                    x2, y2 = x, row + 1
                    line_to_remove = (x1, y1, x2, y2)
                    all_possible_line_segments.remove(line_to_remove)
                if cell.south and cell.is_linked(cell.south):
                    y = row + 1
                    x1, y1 = col, y
                    x2, y2 = col + 1, y
                    line_to_remove = (x1, y1, x2, y2)
                    all_possible_line_segments.remove(line_to_remove)

        # White out the areas where the maze starts and ends from
        for segment in all_possible_line_segments:
            coords = [coord * cell_size for coord in segment]
            drawer.line(coords, width=maze_width, fill=self.fill_black)
        if starting_node:
            self.mark_node_with_tag(starting_node, cell_size, drawer, 'start')
        if ending_node:
            self.mark_node_with_tag(ending_node, cell_size, drawer, 'end')
        if place_on_background:
            image = self.place_maze_on_background(image, image_size)
        return image

    @staticmethod
    def is_cell_on_north_border(cell: Cell) -> bool:
        return cell.row_num == 0

    def is_cell_on_south_border(self, cell: Cell) -> bool:
        return cell.row_num == self.rows - 1

    @staticmethod
    def is_cell_on_west_border(cell: Cell) -> bool:
        return cell.col_num == 0

    def is_cell_on_east_border(self, cell: Cell) -> bool:
        return cell.col_num == self.cols - 1

    def get_set_of_all_possible_line_segments(self):
        segment_set = set()
        for row in self.each_row():
            for col in self.each_col():
                cell = self[row, col]
                if not cell.enabled:
                    continue
                north_segment = (col, row, col + 1, row)
                south_segment = (col, row + 1, col + 1, row + 1)
                west_segment = (col, row, col, row + 1)
                east_segment = (col + 1, row, col + 1, row + 1)
                segment_set.add(north_segment)
                segment_set.add(south_segment)
                segment_set.add(west_segment)
                segment_set.add(east_segment)
        return segment_set

    @staticmethod
    def place_maze_on_background(maze_image: Image, image_size: Tuple[int, int]) -> Image:
        margin = MazeGrid.default_cell_size*2
        background_image_size = (image_size[0] + 2*margin, image_size[1] + 2*margin)
        background = Image.new('RGB', background_image_size, color=MazeGrid.fill_white)
        background.paste(maze_image, (margin, margin))
        return background

    def draw_openings(self, border_node: Tuple[int, int], cell_size: int,
                      drawer: ImageDraw.Draw, border_width: int, tag: str):
        row, col = border_node
        if row == 0:
            start_point = [col * cell_size, 0]
            end_point = [(col + 1) * cell_size, 0]
        elif col == self.cols - 1:
            x = self.rows * cell_size
            start_point = [x, row * cell_size]
            end_point = [x, (row + 1) * cell_size]
        elif row == self.rows - 1:
            y = self.rows * cell_size
            start_point = [col*cell_size, y]
            end_point = [(col + 1) * cell_size, y]
        elif col == 0:
            start_point = [0, row*cell_size]
            end_point = [0, (row+1)*cell_size]
        else:
            raise Exception('Node must be on the border')
        drawer.line(start_point + end_point, width=border_width, fill=self.fill_white)
        drawer.text([col*cell_size + 10, row*cell_size + 5], tag, font=self.load_arial_font(), fill=self.fill_black)

    def mark_node_with_tag(self, node: Tuple[int, int], cell_size: int, drawer: ImageDraw.Draw, tag: str):
        row, col = node
        drawer.text([col*cell_size + 10, row*cell_size + 5], tag, font=self.load_arial_font(), fill=self.fill_black)

    @staticmethod
    def load_arial_font() -> ImageFont:
        base_dir = os.path.dirname(__file__)
        f = os.path.join(base_dir, 'res', 'arial.ttf')
        font = ImageFont.truetype(f, size=25)
        return font

    def configure_cells(self):
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self[(row, col)]
                cell.north = self[row-1, col]
                cell.south = self[row+1, col]
                cell.left = self[row, col-1]
                cell.right = self[row, col+1]

    def __getitem__(self, item) -> Optional[Cell]:
        row, col = item
        if row < 0 or row >= self.rows:
            return None
        if col < 0 or col >= self.cols:
            return None
        return self.grid[row][col]

    def get_random_cell(self) -> Cell:
        cell_seq_num = randint(0, self.enabled_size - 1)
        enabled_seen_so_far = 0
        for row in self.each_row():
            for col in self.each_col():
                cell = self[row, col]
                if cell.enabled:
                    if enabled_seen_so_far == cell_seq_num:
                        return cell
                    else:
                        enabled_seen_so_far += 1

    def size(self):
        return self.rows * self.cols

    def each_row(self):
        for row in range(self.rows):
            yield row

    def each_col(self):
        for col in range(self.cols):
            yield col

    @staticmethod
    def coin_flip() -> str:
        return choice(['heads', 'tails'])

    def generate_bfs_distance_map(self, starting_node: Tuple[int, int]):
        q, next_q = [starting_node], []
        dist_map = {}
        current_dist = 0
        while q:
            selected = q.pop(0)
            dist_map[selected] = current_dist
            cell = self[selected]
            for link in cell.links:
                link_pos = link.pos
                if link_pos in dist_map:
                    continue
                next_q.append(link_pos)

            if not q:
                current_dist += 1
                q = next_q
                next_q = []
        return dist_map

    def determine_nodes_with_greatest_separation(self):
        """ This method will return two nodes that have the greatest distance between them.
        :return:
        """
        random_cell = self.get_random_cell()
        dist_map = self.generate_bfs_distance_map(random_cell.pos)
        first_furthest_node, first_furthest_dist = None, 0

        for node in sorted(dist_map.keys()):
            if dist_map[node] > first_furthest_dist:
                first_furthest_node = node
                first_furthest_dist = dist_map[node]

        dist_map = self.generate_bfs_distance_map(first_furthest_node)
        second_furthest_node, second_furthest_dist = None, 0
        for node in sorted(dist_map.keys()):
            if dist_map[node] > second_furthest_dist:
                second_furthest_node = node
                second_furthest_dist = dist_map[node]
        return first_furthest_node, second_furthest_node

    def determine_nodes_with_greatest_separation_on_border(self):
        dist_map = self.generate_bfs_distance_map((0, 0))
        first_furthest_node, first_furthest_dist = None, 0

        for node in self.get_border_nodes():
            if dist_map[node] > first_furthest_dist:
                first_furthest_node = node
                first_furthest_dist = dist_map[node]

        dist_map = self.generate_bfs_distance_map(first_furthest_node)
        second_furthest_node, second_furthest_dist = None, 0
        for node in self.get_border_nodes():
            if dist_map[node] > second_furthest_dist:
                second_furthest_node = node
                second_furthest_dist = dist_map[node]
        return first_furthest_node, second_furthest_node

    def get_border_nodes(self):
        current_node = (0, 0)
        sequence = [(0, 1),  # go to right
                    (1, 0),  # go down
                    (0, -1),  # to left
                    (-1, 0)]  # to the top

        current_seq = sequence.pop(0)
        while True:
            yield current_node
            next_node = current_node[0] + current_seq[0], current_node[1] + current_seq[1]
            if not self[next_node]:
                current_seq = sequence.pop(0)
                next_node = current_node[0] + current_seq[0], current_node[1] + current_seq[1]
            current_node = next_node
            if current_node == (0, 0):
                break

    def yield_each_cell(self):
        for row in self.each_row():
            for col in self.each_col():
                yield self[row, col]

    @staticmethod
    def create_gif_from_frames(frames: List[Image.Image], file_name: str):
        frames[0].save(file_name, format='gif', save_all=True, append_images=frames[1:], duration=100, loop=0)

    def apply_algorithm(self, video_output_path: str) -> Optional[cv2.VideoWriter]:
        raise NotImplementedError

    def number_of_dead_ends(self):
        count = 0
        for cell in self.yield_each_cell():
            if cell.get_links().__len__() == 1:
                count += 1
        return count

    @staticmethod
    def get_video_writer(starting_frame: Image, output_file_path):
        video_dims = starting_frame.size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_file_path, fourcc, 15, video_dims)
        return video_writer

    @staticmethod
    def write_frame_to_video_writer(writer: cv2.VideoWriter, frame: Image):
        frame_as_np = np.array(frame)
        writer.write(cv2.cvtColor(frame_as_np, cv2.COLOR_RGB2BGR))
