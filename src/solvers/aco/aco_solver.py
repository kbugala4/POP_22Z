import numpy as np
from copy import deepcopy, copy
import random
import sys

sys.path.append("src/")
from solvers.aco.ant import Ant
from problem.sudoku_manager import Sudoku
from constants import SIZE, SEED

rand_object = random.Random(SEED)


class AntColonyOptSolver:
    def __init__(
        self,
        greed_factor=0.9,
        local_pher_factor=0.15,
        global_pher_factor=0.8,
        evaporation=0.005,
    ):
        self.local_pher_factor = local_pher_factor
        self.global_pher_factor = global_pher_factor
        self.greed_factor = greed_factor
        self.evaporation = evaporation

    def solve(self, sudoku: Sudoku, ants_count):
        is_solved = False
        cells_count = SIZE**2
        init_val = 1 / cells_count
        self.pheromone_matrix = np.ones([SIZE, SIZE, SIZE]) * init_val

        epoch = 1
        solution = None
        all_tiles = [index for index, _ in np.ndenumerate(sudoku.board)]
        while not is_solved:
            ants = []
            temp_all_tiles = copy(all_tiles)
            best_pheromone_to_add = 0
            for ant in range(ants_count):
                tile = rand_object.choice(temp_all_tiles)
                temp_all_tiles.remove(tile)
                ants.append(
                    Ant(
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
                    print(
                        f"EPOCH {epoch}: most fixed = {best_ant.sudoku.fixed_count}, failed count: {best_ant.sudoku.failed_count}, sol:\n {solution}"
                    )
                    print("SUDOKU SOLVED")
                    return solution

            pheromone_to_add = cells_count / (cells_count - best_ant_fixed_count)
            # print(f"pheromone_to_add: {pheromone_to_add}")
            if pheromone_to_add > best_pheromone_to_add:
                solution = best_ant.sudoku.board
                best_pheromone_to_add = pheromone_to_add

            # Global pheromone update
            self.global_pher_mat_update(solution, best_pheromone_to_add)

            # Evapropation
            best_pheromone_to_add *= 1 - self.evaporation
            print(
                f"EPOCH {epoch}: most fixed = {best_ant.sudoku.fixed_count}, failed count: {best_ant.sudoku.failed_count}, sol:\n {solution}"
            )
            epoch += 1

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
