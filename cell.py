import random
from typing import Tuple, List, Optional


class Cell(object):
    def __init__(self, row_num: int, col_num: int):
        self.row_num = row_num
        self.col_num = col_num
        self.links = dict()
        self.north, self.south, self.left, self.right = None, None, None, None
        self.enabled = True

    def disable_cell(self):
        self.enabled = False

    def enable_cell(self):
        self.enabled = True

    def link_two_cells(self, other: 'Cell', bidirection=True):
        self.links[other] = True
        if bidirection:
            other.link_two_cells(self, False)

    def unlink_two_cells(self, other: 'Cell', bidirection=True):
        del self.links[other]
        if bidirection:
            other.unlink_two_cells(self, False)

    def get_links(self):
        return self.links.keys()

    def is_linked(self, other: 'Cell') -> bool:
        if other in self.links:
            return self.links[other]
        else:
            return False

    def get_neighbors(self) -> List['Cell']:
        neighbors = []
        for n in [self.north, self.south, self.left, self.right]:
            if n:
                neighbors.append(n)
        return neighbors

    def get_random_neighbor(self) -> 'Cell':
        neighbors = self.get_neighbors()
        return random.sample(neighbors, 1)[0]

    def get_unlinked_neighbors(self) -> List['Cell']:
        """ Will get enabled unlinked neighbors
        :return:
        """
        neighbors = self.get_neighbors()
        unlinked_neighbors = []
        for n in neighbors:
            if not n.get_links() and n.enabled:
                unlinked_neighbors.append(n)
        return unlinked_neighbors

    def get_random_unlinked_neighbor(self) -> Optional['Cell']:
        unlinked_neighbors = self.get_unlinked_neighbors()
        if not unlinked_neighbors:
            return None
        return random.sample(unlinked_neighbors, 1)[0]

    def __eq__(self, other: 'Cell'):
        return self.row_num == other.row_num and self.col_num == other.col_num

    def __hash__(self):
        return hash((self.row_num, self.col_num))

    def __repr__(self):
        return str((self.row_num, self.col_num))

    @property
    def pos(self) -> Tuple[int, int]:
        return self.row_num, self.col_num
