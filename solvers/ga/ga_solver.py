import numpy as np
import random


class GeneticAlgorithmSolver():
    def __init__(self, t_max=600, pc=0.85, pm=0.15, size=400):
        self.t_max = t_max
        self.pc = pc
        self.pm = pm
        self.size = size

    def get_parameters(self):
        params = {
            "t_max": self.t_max,
            "pc": self.pc,
            "pm": self.pm,
            "size": self.size
        }
        return params

    def initialize_p0(self):
        """
        Return random decision vectors
        """
        p0 = np.array([[random.getrandbits(1) for _ in range(200)]
                       for _ in range(self.size)])
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
        probability = scores/np.amax(scores)
        probability = probability/np.sum(probability)
        ids = np.array([i for i in range(self.size)])
        selected_ids = np.random.choice(ids, self.size, p=probability)
        P_selected = np.array([P[ids[i]] for i in selected_ids])
        return P_selected

    def crossover_mutation(self, P):
        """
        Function, that performs crossover for given population
        and then mutates each chromosome, both with given probability
        """
        num_of_pairs = int(self.size/2)
        pairs = []
        ids = [i for i in range(num_of_pairs)]
        while ids:
            rand1 = ids.pop(np.random.randint(0, len(ids)))
            rand2 = ids.pop(np.random.randint(0, len(ids)))
            pair = rand1, rand2
            pairs.append(pair)

        P_crossed = P
        for pair in pairs:
            if random.random() < self.pc:
                cross_bit = np.random.randint(1, num_of_pairs)
                tmp = P_crossed[pair[0]]
                for bit in range(cross_bit, 200):
                    P_crossed[pair[0], bit] = P_crossed[pair[1], bit]
                for bit in range(0, cross_bit):
                    P_crossed[pair[1], bit] = tmp[bit]

        P_mutated = P_crossed
        for i in range(self.size):
            for j in range(200):
                if random.random() < self.pm:
                    P_mutated[i, j] = 1 - P_mutated[i, j]

        return P_mutated

    def solve(self, problem, pop0, *args, **kwargs):
        """
        Solves a given problem for single population0,
        returnes globally best vector of decision, score
        and best score per iteration (for plotting)
        """
        def get_scores(P):
            scores = np.array([problem(x) for x in P])
            return scores

        t = 0
        scores = get_scores(pop0)
        x_best_global, score_best_global = self.find_best(pop0, scores)

        P_t = pop0
        P_t_scores = scores

        best_score_per_iter = []
        while t < self.t_max:
            print(f'I: {t} best: {score_best_global} max: {np.max(P_t_scores)}')

            P_t_selected = self.selection(P_t, P_t_scores)
            P_t_mutated = self.crossover_mutation(P_t_selected)

            P_t = P_t_mutated
            P_t_scores = get_scores(P_t)
            x_best_tmp, score_best_tmp = self.find_best(P_t, P_t_scores)
            if score_best_tmp > score_best_global:
                x_best_global = x_best_tmp
                score_best_global = score_best_tmp
                print(f'Improvement! Score: {score_best_global}')

            best_score_per_iter.append(score_best_tmp)
            t += 1
        return x_best_global, score_best_global, np.array(best_score_per_iter)
