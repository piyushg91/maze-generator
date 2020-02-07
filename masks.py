from maze_fun.maze import MazeGrid
from maze_fun.recursive_backtracker import RecursiveBackTracker
from PIL import Image


class Masks(object):
    @staticmethod
    def create_maze_from_image(image_path: str):
        image = Image.open(image_path)
        bw_image = image.convert('L')
        width, height = image.size
        maze = RecursiveBackTracker(height, width)
        for i in range(width):
            for j in range(height):
                pixel_value = bw_image.getpixel((i, j))
                if pixel_value > 60:
                    maze.disable_cell(j, i)
        return maze

    @staticmethod
    def resize_image(original_image_path: str, output_image_path: str, scaling_factor):
        image = Image.open(original_image_path)
        width, height = image.size
        new_width, new_height = int(scaling_factor*width), int(scaling_factor*height)
        image.thumbnail((new_width, new_height),Image.ANTIALIAS)
        image.save(output_image_path)


if __name__ == '__main__':
    Masks.resize_image('/home/piyush/Downloads/test-heart.png', '/home/piyush/Downloads/test-heart2.png', 0.25)
    maze = Masks().create_maze_from_image('/home/piyush/Downloads/test-heart2.png')
    # frames = maze.apply_algorithm()
    frames = maze.create_maze_path_frames()
