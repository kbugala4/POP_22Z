import numpy as np
import random
from copy import deepcopy, copy
import sys

sys.path.append("src/")
from solvers.aco.ant import Ant
from problem.sudoku_manager import Sudoku
from constants import SIZE


class AntColonyOptSolver:
    def __init__(
        self,
        max_epoch=500,
        greed_factor=0.9,
        local_pher_factor=0.15,
        global_pher_factor=0.8,
        evaporation=0.005,
        seed=None,
    ):
        self.max_epoch = max_epoch
        self.local_pher_factor = local_pher_factor
        self.global_pher_factor = global_pher_factor
        self.greed_factor = greed_factor
        self.evaporation = evaporation
        self.seed = seed
        if seed is None:
            self.rand_object = np.random.RandomState()
            self.rand_choice_obj = random.Random()
        else:
            self.rand_object = np.random.RandomState(seed)
            self.rand_choice_obj = random.Random(seed)

    def solve(self, sudoku: Sudoku, ants_count):
        is_solved = False
        cells_count = SIZE**2
        init_val = 1 / cells_count
        self.pheromone_matrix = np.ones([SIZE, SIZE, SIZE]) * init_val

        ants_moves = 0
        best_score_per_epoch = []

        epoch = 1
        solution = None
        all_tiles = [index for index, _ in np.ndenumerate(sudoku.board)]
        while epoch < self.max_epoch and not is_solved:
            ants = []
            temp_all_tiles = copy(all_tiles)
            best_pheromone_to_add = 0
            for ant in range(ants_count):
                tile = self.rand_choice_obj.choice(temp_all_tiles)
                temp_all_tiles.remove(tile)
                ants.append(
                    Ant(
                        self.rand_choice_obj,
                        deepcopy(sudoku),
                        self.pheromone_matrix,
                        init_val,
                        self.local_pher_factor,
                        self.greed_factor,
                        tile,
                    )
                )

            for _ in range(cells_count):
                for ant in ants:
                    if ant.tile_is_valid():
                        number = ant.choose_value()
                        ant.propagate_constraints(number)
                    ant.move_next()
                    ants_moves += 1

            # Finding best ant
            best_ant_fixed_count = 0
            for ant in ants:
                fixed_count = ant.sudoku.fixed_count

                # Check if best ant for this epoch
                if fixed_count > best_ant_fixed_count:
                    best_ant = ant
                    best_ant_fixed_count = fixed_count

                # Check if is solved
                if fixed_count == cells_count:
                    solution = ant.sudoku.board
                    is_solved = True
                    break

            if not is_solved:
                pheromone_to_add = cells_count / (cells_count - best_ant_fixed_count)
                if pheromone_to_add > best_pheromone_to_add:
                    solution = best_ant.sudoku.board
                    best_pheromone_to_add = pheromone_to_add

            # Global pheromone update
            self.global_pher_mat_update(solution, best_pheromone_to_add)

            # Evaporation
            best_pheromone_to_add *= 1 - self.evaporation
            print(
                f"EPOCH {epoch}: most fixed = {best_ant.sudoku.fixed_count}, failed count: {best_ant.sudoku.failed_count}"
            )
            best_score_per_epoch.append(best_ant.sudoku.fixed_count)
            epoch += 1

        if is_solved:
            print(f"Problem solved. Solution:\n{solution}\n")
        else:
            print(f"Unsolved. Best solution:\n{solution}\n")
        return (
            solution,
            best_ant.sudoku.fixed_count,
            np.array(best_score_per_epoch),
            ants_moves,
        )

    def global_pher_mat_update(self, solution, best_pheromone):
        for row in range(SIZE):
            for col in range(SIZE):
                set_value = solution[row, col]
                if set_value > 0:
                    self.pheromone_matrix[row, col][set_value - 1] *= (
                        1 - self.global_pher_factor
                    )
                    self.pheromone_matrix[row, col][set_value - 1] += (
                        self.global_pher_factor * best_pheromone
                    )
