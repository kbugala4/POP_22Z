import numpy as np
import matplotlib.pyplot as plt
import json
import os
import sys

sys.path.append("src/")
from solvers.aco.aco_solver import AntColonyOptSolver
from problem.sudoku_manager import Sudoku
from time import perf_counter
from statistics import mean

ABS_PATH = os.path.dirname(__file__)

TEST_FILE = "test_aco_nr_16.json"

with open(os.path.join(ABS_PATH, f"../../results/params/aco/{TEST_FILE}")) as json_file:
    params = json.load(json_file)


sudokus_range = range(params["start_id"], params["start_id"] + params["num_of_sudokus"])

sudokus = [Sudoku(params["sudoku_level"], id) for id in sudokus_range]


solver = AntColonyOptSolver(
    max_epoch=params["max_epoch"],
    greed_factor=params["greed_factor"],
    local_pher_factor=params["local_pher_factor"],
    global_pher_factor=params["global_pher_factor"],
    evaporation=params["evaporation"],
    seed=params["seed"],
)


def test_aco_solver(solver, sudokus):
    solutions_list = []
    best_scores_list = []
    best_per_iters = []
    ants_moves_list = []
    exec_times = []
    for i in range(params["num_of_sudokus"]):
        print(f"Sudoku to solve:\n{sudokus[i].board}\n")
        for j in range(params["num_of_runs"]):
            start_time = perf_counter()
            results = solver.solve(sudoku=sudokus[i], ants_count=params["ants_count"])
            exec_times.append(perf_counter() - start_time)
            solutions_list.append(results[0])
            best_scores_list.append(results[1])
            best_per_iters.append(results[2])
            ants_moves_list.append(results[3])
    return solutions_list, best_scores_list, best_per_iters, ants_moves_list, exec_times


solutions, best_scores, best_per_iters, ants_moves_list, exec_times = test_aco_solver(
    solver, sudokus
)


MAX_STEPS = max([len(bests) for bests in best_per_iters])
avg_steps = mean([len(bests) for bests in best_per_iters])


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


avg_ants_moves = mean(ants_moves_list)


avg_exec_time = mean(exec_times)


params_text = "max_epoch={}, greed_factor={}, local_pher_f={}, global_pher_f={}, evaporation={}, ants_count={}".format(
    params["max_epoch"],
    params["greed_factor"],
    params["local_pher_factor"],
    params["global_pher_factor"],
    params["evaporation"],
    params["ants_count"],
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
    "Test nr {} (ACO): Przyrost wartości funkcji celu".format(params["test_id"])
)
plt.title(
    "Średni wynik: {}, średni czas: {:.2f}, średnia l. kroków mrówek: {:.2f}, średnia l. epok: {:.2f}".format(
        avg_best_score, avg_exec_time, avg_ants_moves, avg_steps
    )
)
plt.figtext(
    0.5, -0.05, params_text, wrap=True, horizontalalignment="center", fontsize=10
)
plt.show()
