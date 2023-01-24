import random
import sys
import numpy as np

sys.path.append("src/")
from problem.sudoku_manager import Sudoku
from constants import SIZE, SEED

rand_object = random.Random(SEED)


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
        new_row = self.tile[0]
        new_col = self.tile[1] + 1

        if new_col >= SIZE:
            new_col = 0
            new_row += 1
        if new_row >= SIZE:
            new_row = 0

        self.tile = (new_row, new_col)

    def choose_value(self):
        pher = self.pheromone_mat[:][self.tile]

        best_pheromone = 0
        available_values = np.array(list(self.sudoku.state[self.tile]))

        # Greedy selection
        if rand_object.random() > self.greed:
            for value in available_values:
                if pher[value - 1] > best_pheromone:
                    best_value = value
                    best_pheromone = pher[value - 1]
            selected_value = best_value

        # Roulette wheel selection
        else:
            weights = pher[available_values - 1]

            selected_value = rand_object.choices(
                available_values, weights=tuple(weights)
            )[0]

        return selected_value

    def propagate_constraints(self, tile_num):
        self.sudoku.update_state(self.tile, tile_num)
        self.update_local(tile_num)

    def update_local(self, tile_num):
        tile_num -= 1
        self.pheromone_mat[tile_num][self.tile] = (
            1 - self.local_pher_update
        ) * self.pheromone_mat[tile_num][
            self.tile
        ] + self.local_pher_update * self.initial_pher_val

    def tile_is_valid(self):
        # print(f"self tile: {self.tile}")
        if self.tile not in self.sudoku.state.keys():
            # print("not valid (a)")
            return False
        elif len(self.sudoku.state[self.tile]) > 1:
            # print("valid")
            return True
        else:
            # print("not valid (b)")
            return False
