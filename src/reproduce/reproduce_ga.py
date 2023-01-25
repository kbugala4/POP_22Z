import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys

sys.path.append("src/")
from solvers.ga.ga_solver import GeneticAlgorithmSolver
from problem.sudoku_manager import Sudoku
from time import perf_counter
from statistics import mean

ABS_PATH = os.path.dirname(__file__)

TEST_FILE = "test_ga_nr_15.json"

with open(os.path.join(ABS_PATH, f"../../results/params/ga/{TEST_FILE}")) as json_file:
    params = json.load(json_file)


sudokus_range = range(params["start_id"], params["start_id"] + params["num_of_sudokus"])

suds_easy = [Sudoku("easy", id) for id in sudokus_range]
suds_medium = [Sudoku("medium", id) for id in sudokus_range]
suds_hard = [Sudoku("hard", id) for id in sudokus_range]


solver = GeneticAlgorithmSolver(
    pop_size=params["pop_size"],
    pc=params["pc"],
    pm=params["pm"],
    max_epoch=params["max_epoch"],
    reset_condition_val=params["reset_cond"],
    succession_rate=params["succ_rate"],
    seed=params["seed"],
)


def test_ga_solver(solver, sudokus, candidates):
    best_chrom_list = []
    best_scores_list = []
    best_per_iters = []
    exec_times = []
    for i in range(params["num_of_sudokus"]):
        print(f"Sudoku to solve:\n{sudokus[i].board}\n")
        for j in range(params["num_of_runs"]):
            start_time = perf_counter()
            results = solver.solve(sudoku=sudokus[i], is_candidate_mode=candidates)
            exec_times.append(perf_counter() - start_time)
            best_chrom_list.append(results[0])
            best_scores_list.append(results[1])
            best_per_iters.append(results[2])
    return best_chrom_list, best_scores_list, best_per_iters, exec_times


best_chroms, best_scores, best_per_iters, exec_times = test_ga_solver(
    solver, suds_easy, candidates=params["if_candidates"]
)


MAX_STEPS = max([len(bests) for bests in best_per_iters])


def normalize_arr(arr):
    if arr.shape[0] == MAX_STEPS:
        return arr
    else:
        norm_arr = np.zeros((MAX_STEPS,))
        norm_arr[: len(arr)] = arr
        norm_arr[len(arr) :] = max(arr)
        return norm_arr


def normalize_best_per_iters(best_per_iters):
    best_iters_avg = []
    best_iters_max = []
    best_iters_min = []
    normalized_best_iters = np.array([normalize_arr(bests) for bests in best_per_iters])
    for i in range(normalized_best_iters.shape[1]):
        best_iters_avg.append(mean(normalized_best_iters[:, i]))
        best_iters_max.append(max(normalized_best_iters[:, i]))
        best_iters_min.append(min(normalized_best_iters[:, i]))
    return best_iters_avg, best_iters_max, best_iters_min


best_per_iters_avg, best_per_iters_max, best_per_iters_min = normalize_best_per_iters(
    best_per_iters
)


avg_best_score = mean(best_scores)


avg_exec_time = mean(exec_times)


params_text = (
    "pop_size={}, pc={}, pm={}, reset_cond={}, succ_rate={}, candidates={}".format(
        params["pop_size"],
        params["pc"],
        params["pm"],
        params["reset_cond"],
        params["succ_rate"],
        params["if_candidates"],
    )
)


plt.figure()
plt.fill_between(
    range(MAX_STEPS),
    best_per_iters_min,
    best_per_iters_max,
    color="b",
    alpha=0.2,
    label="min to max",
)
plt.plot(range(MAX_STEPS), (best_per_iters_avg), "r", label="avg best scores")
plt.legend(loc="lower right")
plt.xlabel("epoch")
plt.ylabel("global score")
plt.suptitle(
    "Test nr {} (GA): Przyrost wartości funkcji celu".format(params["test_id"])
)
plt.title(
    "Średnia najlepsza wartość: {}, średni czas wykonania: {:.2f}".format(
        avg_best_score, avg_exec_time
    )
)
plt.figtext(
    0.5, -0.05, params_text, wrap=True, horizontalalignment="center", fontsize=10
)
plt.show()
