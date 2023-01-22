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

    def set_value(self):
        pass

    def propagate_constraints(self):
        pass

    def update_local(self):
        pass
