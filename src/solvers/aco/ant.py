import random
import sys
import numpy as np

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
        next_col = self.tile[1] + 1
        if next_col <= 8:
            self.tile[1] += 1
        else:
            self.tile[0] += 1
            self.tile[1] = 0

    def choose_value(self):
        pher = self.pheromone_mat[self.tile[0]][self.tile[1]]

        best_pheromone = 0
        available_values = self.sudoku.state[self.tile]

        # Greedy selection
        if random.random() > self.greed:
            for value in available_values:
                if pher[value - 1] > best_pheromone:
                    best_value = value
                    best_pheromone = pher[value - 1]
            selected_value = best_value

        # Roulette wheel selection
        else:
            selected_value = random.choices(available_values, cum_weights=pher)

        return selected_value

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
