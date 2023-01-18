from dokusan import generators
import numpy as np
import os

ABS_PATH = os.path.dirname(__file__)


class SudokuManager(object):
    SIZE = 9

    def __init__(self):
        self.sudoku_levels = {"easy": 50, "medium": 150, "hard": 250}

    def generate_boards(self, num_of_gen, level):
        for i in range(num_of_gen):
            board = generators.random_sudoku(avg_rank=self.sudoku_levels[level])
            board_arr = np.array(list(str(board)), dtype=int).reshape(
                self.SIZE, self.SIZE
            )

            with open(
                os.path.join(ABS_PATH, f"sudoku_boards/{level}/sudoku_{level}_{i}.npy"),
                "wb",
            ) as f:
                np.save(f, board_arr)

    def load_sudoku(self, filepath):
        with open(filepath, "rb") as f:
            board = np.load(f)
        return board

    def load_n_level_boards(self, level, n_boards):
        directory = os.path.join(ABS_PATH, "sudoku_boards/" + level)
        boards_list = []
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                board = self.load_sudoku(f)
            boards_list.append(board)
            if len(boards_list) >= n_boards:
                break
        return boards_list
