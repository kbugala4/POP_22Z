import random
import sys

sys.path.append("src/")
from problem.sudoku_manager import Sudoku


class Ant:
    def __init__(
        self,
        sudoku: Sudoku,
        pheromone_mat=None,
        initial_pher_val=0.0,
        local_pher_update=0.0,
        greed=1.0,
        tile=(0, 0),
    ):
        self.sudoku = sudoku
        self.pheromone_mat = pheromone_mat
        self.initial_pher_val = initial_pher_val
        self.local_pher_update = local_pher_update
        self.greed = greed
        self.tile = tile

    def move_next(self):
        pass

    def choose_value(self):
        pass

    def propagate_constraints(self, tile_num):
        self.sudoku.update_state(self.tile, tile_num)

    def update_local(self, tile_num):
        self.pheromone_mat[tile_num][self.tile] = (
            1 - self.local_pher_update
        ) * self.pheromone_mat[
            tile_num
        ] + self.local_pher_update * self.initial_pher_val

    def tile_is_valid(self):
        if not self.sudoku.state[self.tile]:
            return False
        elif len(self.sudoku.state[self.tile]) > 1:
            return True
        else:
            return False
