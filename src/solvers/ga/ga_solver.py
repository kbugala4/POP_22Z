import numpy as np
from copy import copy
import random
import sys

sys.path.append("src/")
from problem.sudoku_manager import Sudoku
from constants import SIZE, BLOCK_SIZE, SEED

rand_object = random.Random(SEED)
rand_np_object = np.random.RandomState(SEED)


class GeneticAlgorithmSolver:
    def __init__(
        self,
        # sudoku: Sudoku,
        pop_size,
        pc=0.85,
        pm=0.15,
        max_epoch=600,
        reset_condition_val=75,
        succession_rate=1.0,
    ):
        self.max_epoch = max_epoch
        self.pc = pc
        self.pm = pm
        self.pop_size = pop_size
        self.reset_condition_val = reset_condition_val
        self.succession_rate = succession_rate

    def generate_chrom(self, is_candidate_mode=False):
        """
        A method to generate chromosome as initial sudoku board.
        Generated chromosome repects constraints for each row
        (row contains all unique numbers 1, 2, 3.. 9).
        Sudoku constraints for columns and block are not applied
        """
        chrom = copy(self.sudoku.board)
        if is_candidate_mode:
            for tile in self.sudoku_state:
                chrom[tile] = rand_object.choice(list(self.sudoku_state[tile]))
            return chrom

        for row_id in range(chrom.shape[0]):
            left_in_row = copy(self.sudoku.nums_left[row_id])
            rand_object.shuffle(left_in_row)
            for i in range(len(chrom[row_id])):
                if chrom[row_id, i] == 0:
                    chrom[row_id, i] = left_in_row.pop()
        return chrom

    def generate_population(self, is_candidate_mode):
        """
        A method to generate population zero based on self.pop_size
        """
        return [self.generate_chrom(is_candidate_mode) for _ in range(self.pop_size)]

    def evaluate_chrom(self, chrom):
        """
        A method to evaluate given chromosome.
        """
        unique_count = 0

        for row in chrom:
            unique_count_row = len(np.unique(row))
            unique_count += unique_count_row

        for col in chrom.T:
            unique_count_col = len(np.unique(col))
            unique_count += unique_count_col

        for i in range(3):
            for j in range(3):
                block = chrom[
                    i * BLOCK_SIZE : i * BLOCK_SIZE + BLOCK_SIZE,
                    j * BLOCK_SIZE : j * BLOCK_SIZE + BLOCK_SIZE,
                ]

                unique_count_block = len(np.unique(block))
                unique_count += unique_count_block

        return unique_count

    def get_parameters(self):
        params = {
            "max_epoch": self.max_epoch,
            "pc": self.pc,
            "pm": self.pm,
            "pop_size": self.pop_size,
            "sudoku": self.sudoku,
            "reset_condition": self.reset_condition_val,
        }
        return params

    def find_best(self, P, scores):
        """
        P, scores are np.arrays
        """
        id_max = np.argmax(scores)
        x_best = P[id_max]
        score_best = scores[id_max]
        return x_best, score_best

    def selection(self, P, scores, is_candidate_mode=False):
        """
        Shifting the score, so there cannot be negative value
        Selecting better scores with higher probability
        """
        scores = scores - np.amin(scores)
        probability = scores / np.amax(scores)
        probability = probability / np.sum(probability)
        ids = np.array([i for i in range(self.pop_size)])
        selected_ids = rand_np_object.choice(ids, self.pop_size, p=probability)
        P_selected = np.array([P[ids[i]] for i in selected_ids])
        if self.succession_rate < 1:
            random_rate = 1 - self.succession_rate
            for i in range(int(random_rate * self.pop_size)):
                P_selected[i] = self.generate_chrom(is_candidate_mode)
        return P_selected

    def mutate(self, chrom, is_candidate_mode):
        if is_candidate_mode:
            for tile in self.sudoku_state:
                if rand_object.uniform(0, 1) < self.pm:  # if row is to mutate
                    chrom[tile] = rand_object.choice(list(self.sudoku_state[tile]))
            return chrom

        row_iterator = 0
        for row in chrom:
            if rand_object.uniform(0, 1) < self.pm:  # if row is to mutate
                available_tiles_row = self.sudoku.free_tiles[row_iterator]
                if len(available_tiles_row) >= 2:
                    tile_a_id = rand_object.choice(available_tiles_row)
                    tile_b_id = rand_object.choice(available_tiles_row)
                    while tile_a_id == tile_b_id:
                        tile_b_id = rand_object.choice(available_tiles_row)
                    temp_number = row[tile_a_id]
                    row[tile_a_id] = row[tile_b_id]
                    row[tile_b_id] = temp_number
            row_iterator += 1
        return chrom

    def cross(self, chrom_a, chrom_b):
        if rand_object.uniform(0, 1) < self.pc:  # if pair is to cross
            slice_p_1 = rand_np_object.randint(0, chrom_a.shape[0])
            slice_p_2 = rand_np_object.randint(0, chrom_a.shape[0])
            while slice_p_1 == slice_p_2:
                slice_p_2 = rand_np_object.randint(1, chrom_a.shape[0])
            if slice_p_2 < slice_p_1:
                slice_p_temp = slice_p_1
                slice_p_1 = slice_p_2
                slice_p_2 = slice_p_temp

            temp_a = copy(chrom_a[slice_p_1:slice_p_2])
            chrom_a[slice_p_1:slice_p_2] = chrom_b[slice_p_1:slice_p_2]
            chrom_b[slice_p_1:slice_p_2] = temp_a
        return chrom_a, chrom_b

    def crossover_mutation(self, P, is_candidate_mode):
        """
        Function, that performs crossover for given population
        and then mutates each chromosome, both with given probability
        """
        pairs = []
        ids = [i for i in range(self.pop_size)]
        while ids:
            rand1 = ids.pop(rand_np_object.randint(0, len(ids)))
            rand2 = ids.pop(rand_np_object.randint(0, len(ids)))
            pair = rand1, rand2
            pairs.append(pair)

        P_crossed = P
        for pair in pairs:
            P_crossed[pair[0]], P_crossed[pair[1]] = self.cross(P[pair[0]], P[pair[1]])

        P_mutated = P_crossed
        for chrom_id in range(self.pop_size):
            P_mutated[chrom_id] = self.mutate(P_mutated[chrom_id], is_candidate_mode)

        return P_mutated

    def solve(self, sudoku: Sudoku, is_candidate_mode=False):
        """
        Solves a given problem for single population0,
        returnes globally best vector of decision, score
        and best score per iteration (for plotting)
        """
        self.sudoku = sudoku
        self.sudoku_state = self.sudoku.get_full_state()

        def get_scores(P):
            scores = np.array([self.evaluate_chrom(x) for x in P])
            return scores

        epoch = 0
        best_score_global = 0
        reset_condition = 0
        reset_history = []
        is_solved = False

        P_epoch = self.generate_population(is_candidate_mode)
        P_epoch_scores = get_scores(P_epoch)

        best_score_per_epoch = []

        while epoch < self.max_epoch or is_solved:
            P_epoch_selected = self.selection(
                P_epoch, P_epoch_scores, is_candidate_mode
            )
            P_epoch_mutated = self.crossover_mutation(
                P_epoch_selected, is_candidate_mode
            )
            P_epoch = P_epoch_mutated

            P_epoch_scores = get_scores(P_epoch)
            best_chrom_local, best_score_local = self.find_best(P_epoch, P_epoch_scores)

            if best_score_local > best_score_global:
                best_chrom_global = best_chrom_local
                best_score_global = best_score_local
                if best_score_global == 3 * SIZE**2:
                    print(f"Problem solved. Solution:\n{best_chrom_global}")
                else:
                    print(f"Improvement! Score: {best_score_global}/243")
                reset_condition = 0

            print(
                f"Epoch: {epoch} best_global: {best_score_global}/243, best_local: {best_score_local}/243"
            )

            best_score_per_epoch.append(best_score_local)
            epoch += 1
            reset_condition += 1

            if reset_condition == self.reset_condition_val:
                print(
                    f"No improvement. Best solution:\n{best_chrom_global} \nGenerating new population."
                )
                P_epoch = self.generate_population(is_candidate_mode)
                P_epoch_scores = get_scores(P_epoch)
                reset_history.append((best_chrom_global, best_score_global))
                best_score_global = 0

        return (
            best_chrom_global,
            best_score_global,
            np.array(best_score_per_epoch),
            reset_history,
        )
