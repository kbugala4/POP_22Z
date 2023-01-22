import numpy as np
from copy import copy
import random
import sys

sys.path.append("src/")
from problem.sudoku_manager import Sudoku


class GeneticAlgorithmSolver:
    def __init__(
        self,
        sudoku: Sudoku,
        pop_size,
        chrom_size,
        pc=0.85,
        pm=0.15,
        t_max=600,
        reset_condition_val=75,
    ):
        self.t_max = t_max
        self.pc = pc
        self.pm = pm
        self.pop_size = pop_size
        self.chrom_size = chrom_size
        self.sudoku = sudoku
        self.reset_condition_val = reset_condition_val

    def generate_chrom(self):
        chrom = copy(self.sudoku.board)
        for row_id in range(chrom.shape[0]):
            left_in_row = copy(self.sudoku.nums_left[row_id])
            random.shuffle(left_in_row)
            for i in range(len(chrom[row_id])):
                if chrom[row_id, i] == 0:
                    chrom[row_id, i] = left_in_row.pop()
        return chrom

    def generate_population(self):
        population = []
        for _ in range(self.pop_size):
            population.append(self.generate_chrom())
        return population

    def evaluate_chrom(self, chrom):
        unique_count = 0
        for col in chrom.T:
            unique_count += 2 * len(np.unique(col))
        for i in range(3):
            for j in range(3):
                block = chrom[i * 3 : i * 3 + 3, j * 3 : j * 3 + 3]
                unique_count += len(np.unique(block))
        return unique_count

    def get_parameters(self):
        params = {
            "t_max": self.t_max,
            "pc": self.pc,
            "pm": self.pm,
            "pop_size": self.pop_size,
        }
        return params

    def initialize_p0(self):
        """
        Return random decision vectors
        """
        p0 = np.array(
            [
                [random.getrandbits(1) for _ in range(self.chrom_size)]
                for _ in range(self.pop_size)
            ]
        )
        return p0

    def find_best(self, P, scores):
        """
        P, scores are np.arrays
        """
        id_max = np.argmax(scores)
        x_best = P[id_max]
        score_best = scores[id_max]
        return x_best, score_best

    def selection(self, P, scores):
        """
        Shifting the score, so there cannot be negative value
        Selecting better scores with higher probability
        """
        scores = scores - np.amin(scores)
        probability = scores / np.amax(scores)
        probability = probability / np.sum(probability)
        ids = np.array([i for i in range(self.pop_size)])
        selected_ids = np.random.choice(ids, self.pop_size, p=probability)
        P_selected = np.array([P[ids[i]] for i in selected_ids])
        return P_selected

    def mutate(self, chrom):
        row_iterator = 0
        for row in chrom:
            if np.random.uniform(0, 1) < self.pm:  # if row is to mutate
                available_tiles_row = self.sudoku.free_tiles[row_iterator]
                if len(available_tiles_row) >= 2:
                    tile_a_id = random.choice(available_tiles_row)
                    tile_b_id = random.choice(available_tiles_row)
                    while tile_a_id == tile_b_id:
                        tile_b_id = random.choice(available_tiles_row)
                    temp_number = row[tile_a_id]
                    row[tile_a_id] = row[tile_b_id]
                    row[tile_b_id] = temp_number
            row_iterator += 1
        return chrom

    def cross(self, chrom_a, chrom_b):
        if np.random.uniform(0, 1) < self.pc:  # if pair is to cross
            slice_point = np.random.randint(1, chrom_a.shape[0])
            temp_a = copy(chrom_a[slice_point:])
            chrom_a[slice_point:] = chrom_b[slice_point:]
            chrom_b[slice_point:] = temp_a
        return chrom_a, chrom_b

    def crossover_mutation(self, P):
        """
        Function, that performs crossover for given population
        and then mutates each chromosome, both with given probability
        """
        num_of_pairs = int(self.pop_size / 2)
        pairs = []
        ids = [i for i in range(self.pop_size)]
        while ids:
            rand1 = ids.pop(np.random.randint(0, len(ids)))
            rand2 = ids.pop(np.random.randint(0, len(ids)))
            pair = rand1, rand2
            pairs.append(pair)

        P_crossed = P
        for pair in pairs:
            P_crossed[pair[0]], P_crossed[pair[1]] = self.cross(P[pair[0]], P[pair[1]])

        P_mutated = P_crossed
        for chrom_id in range(self.pop_size):
            P_mutated[chrom_id] = self.mutate(P_mutated[chrom_id])

        return P_mutated

    def solve(self, *args, **kwargs):
        """
        Solves a given problem for single population0,
        returnes globally best vector of decision, score
        and best score per iteration (for plotting)
        """

        def get_scores(P):
            scores = np.array([self.evaluate_chrom(x) for x in P])
            return scores

        t = 0
        reset_condition = 0
        pop0 = self.generate_population()
        scores = get_scores(pop0)
        x_best_global, score_best_global = self.find_best(pop0, scores)

        P_t = pop0
        P_t_scores = scores
        global_best = []

        best_score_per_iter = []
        while t < self.t_max:
            print(f"I: {t} best: {score_best_global} max: {np.max(P_t_scores)}")

            P_t_selected = self.selection(P_t, P_t_scores)
            P_t_mutated = self.crossover_mutation(P_t_selected)

            P_t = P_t_mutated
            P_t_scores = get_scores(P_t)
            x_best_tmp, score_best_tmp = self.find_best(P_t, P_t_scores)
            if score_best_tmp > score_best_global:
                x_best_global = x_best_tmp
                score_best_global = score_best_tmp
                print(f"Improvement! Score: {score_best_global}")
                reset_condition = 0

            best_score_per_iter.append(score_best_tmp)
            t += 1
            reset_condition += 1
            if reset_condition == self.reset_condition_val:
                print("No improvement. Generating new population.")
                P_t = self.generate_population()
                P_t_scores = get_scores(P_t)
                global_best.append((x_best_global, score_best_global))
                score_best_global = 0

        return x_best_global, score_best_global, np.array(best_score_per_iter)