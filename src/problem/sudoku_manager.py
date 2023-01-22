from dokusan import generators
import numpy as np
import os
import sys
from copy import copy

sys.path.append("src/")
from constants import *

ABS_PATH = os.path.dirname(__file__)


def generate_boards(num_of_gen, level):
    for i in range(num_of_gen):
        board = generators.random_sudoku(avg_rank=SUDOKU_LEVELS[level])
        board_arr = np.array(list(str(board)), dtype=int).reshape(SIZE, SIZE)
        with open(
            os.path.join(ABS_PATH, f"sudoku_boards/{level}/sudoku_{level}_{i}.npy"),
            "wb",
        ) as f:
            np.save(f, board_arr)


class Sudoku(object):
    def __init__(self, level, board_id):
        directory = os.path.join(ABS_PATH, f"sudoku_boards/" + level)
        filename = os.path.join(directory, f"sudoku_{level}_{board_id}.npy")
        try:
            with open(filename, "rb") as f:
                self.board = np.load(f)
        except OSError as e:
            print(
                f"There is no board with level: {level} and board_id: {board_id}: {e}",
                file=sys.stderr,
            )
            return

        self.free_tiles, self.nums_left = self.get_free_in_rows()
        self.fixed_count = len(self.__get_occupied_tiles())
        self.failed_count = 0
        self.state = self.get_full_state()

    def __get_free_tiles(self):
        free_tiles_arrs = np.where(self.board == 0)
        return list(zip(free_tiles_arrs[0], free_tiles_arrs[1]))

    def __get_occupied_tiles(self):
        occ_tiles_arrs = np.where(self.board != 0)
        return list(zip(occ_tiles_arrs[0], occ_tiles_arrs[1]))

    def __check_row(self, possible_nums, tile):
        for num in self.board[tile[0], :]:
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    def __check_column(self, possible_nums, tile):
        for num in self.board[:, tile[1]]:
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    def __block_left_up_corner(self, tile):
        return tuple(
            BLOCK_SIZE * np.array([tile[0] // BLOCK_SIZE, tile[1] // BLOCK_SIZE])
        )

    def __check_block(self, possible_nums, tile):
        left_up_corner = self.__block_left_up_corner(tile)
        for num in self.board[
            left_up_corner[0] : left_up_corner[0] + BLOCK_SIZE,
            left_up_corner[1] : left_up_corner[1] + BLOCK_SIZE,
        ].flatten():
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    def get_full_state(self):
        state = {}
        # for tile, _ in np.ndenumerate(self.board):
        for tile in self.__get_free_tiles():
            numbers = copy(NUMBERS)
            numbers = self.__check_row(numbers, tile)
            numbers = self.__check_column(numbers, tile)
            numbers = self.__check_block(numbers, tile)
            state[tile] = numbers
            if len(numbers) == 1:
                self.board[tile] = list(numbers)[0]
                self.fixed_count += 1
            elif len(numbers) == 0:
                self.failed_count += 1
        return state

    def update_state(self, upd_tile, tile_num):
        if len(self.state[upd_tile]) > 0:
            new_fixed_tiles = []
            self.board[upd_tile] = tile_num
            self.state[upd_tile] = {tile_num}
            self.fixed_count += 1
            for tile in self.state.keys():
                if (
                    tile != upd_tile
                    and (
                        tile[0] == upd_tile[0]
                        or tile[1] == upd_tile[1]
                        or self.__block_left_up_corner(tile)
                        == self.__block_left_up_corner(upd_tile)
                    )
                    and tile_num in self.state[tile]
                ):
                    # print(f"Before remove: {self.state[tile]}")
                    self.state[tile].remove(tile_num)
                    # print(f"After remove: {self.state[tile]}")
                    # print(f"Removing {tile_num} from {tile}")
                    if not self.state[tile]:
                        # print(f"Tile {tile} set as failed")
                        self.failed_count += 1
                        self.fixed_count -= 1
                    elif len(self.state[tile]) == 1:
                        # print(f"Tile {tile} set as fixed")
                        # self.fixed_count += 1
                        new_fixed_tiles.append((tile, list(self.state[tile])[0]))
            for new_fixed in new_fixed_tiles:
                self.update_state(new_fixed[0], new_fixed[1])

    def get_left_numbers(self):
        numbers_left = []
        for i in NUMBERS:
            for _ in range(9 - (self.board == i).sum()):
                numbers_left.append(i)
        return numbers_left

    def __get_left_in_row(self, row_id):
        numbers_left = []
        for i in NUMBERS:
            if i not in self.board[row_id]:
                numbers_left.append(i)
        return numbers_left

    def get_free_in_rows(self):
        free_ids = {}
        nums_left = {}
        for i in range(self.board.shape[0]):
            free_ids[i] = np.where(self.board[i] == 0)[0].tolist()
            nums_left[i] = self.__get_left_in_row(i)
        return free_ids, nums_left


if __name__ == "__main__":

    sud1 = Sudoku("easy", 4)

    print(sud1.board)

    print(sud1.state)

    sud1.update_state((0, 0), 3)

    print("AFTER UPDATE:")

    print(sud1.state)

    print(sud1.board)

    arr = np.zeros((3, 4, 5))
    print(arr)
    arr[0, 1, 2] = 45
    arr[0][(1, 2)] = 45
    print(arr)
