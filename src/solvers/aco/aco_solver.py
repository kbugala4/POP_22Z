import numpy as np
from copy import copy
import random
import sys

sys.path.append("src/")
from solvers.aco.ant import Ant
from problem.sudoku_manager import Sudoku
from constants import SIZE

class AntColonyOptSolver:
    def __init__(
        self,
        greed_factor=0.9,
        local_pher_factor=0.1,
        global_pher_factor=0.9,
        evapropation=0.005
    ):
        # self.sudoku = sudoku
        self.local_pher_factor = local_pher_factor
        self.global_pher_factor = global_pher_factor
        self.greed_factor = greed_factor
        self.evapropation = evapropation

    def solve(self, sudoku: Sudoku):
        is_solved = False
        cells_count = SIZE**2
        init_val = 1 / cells_count
        
        self.pheromone_matrix = [[[init_val for _ in range(SIZE)]
                        for _ in range(SIZE)]
                        for _ in range(SIZE)]

        ants = [Ant() for _ in range(cells_count)]
        epoch = 1
        while not is_solved:
            for ant in range(cells_count):
                column =  ant % SIZE
                row = int(ant / SIZE)
                pose = (row, column)
                ants[ant] = Ant()

            for step in range(cells_count):
                for ant in ants:
                    if ant.cell_to_set():
                        ant.decide_and_propagate()
                    ant.move_next()
            
            # Finding best ant
            most_fixed = 0
            for ant in ants:
                fixed_count = ant.sudoku.fixed_count
                failed_count = ant.sudoku.failed_count

                # Check if is solved
                if failed_count == 0:
                    solution = ant.sudoku.board
                    is_solved = True

                # Check if best ant for this epoch
                if fixed_count > most_fixed:
                    best_ant = ant
                    best_ant_fixed_count = fixed_count

            pheromone_to_add = cells_count / (cells_count - best_ant_fixed_count)

            if pheromone_to_add > best_pheromone_to_add:
                solution = best_ant.sudoku.board
                best_pheromone_to_add = pheromone_to_add

            # Global pheromone update
            self.global_pher_mat_update(solution, best_pheromone_to_add)

            # Evapropation
            best_pheromone_to_add *= (1 - self.evaporation)
            epoch += 1

    def global_pher_mat_update(self, solution, best_pheromone):
        for row in range(SIZE):
            for col in range(SIZE):
                set_value = solution[row, col]
                if set_value > 0:
                    self.pheromone_matrix[row, col][set_value - 1] *= (1 - self.self.global_pher_factor) 
                    self.pheromone_matrix[row, col][set_value - 1] += self.self.global_pher_factor * best_pheromone