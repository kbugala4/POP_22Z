from copy import copy
import numpy as np
import sys


class Sudoku(object):
    NUMBERS = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    BLOCK_SIZE = 3

    def __init__(self, board):
        self.board = board
        self.free_tiles, self.nums_left = self.get_free_in_rows()

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

    def __check_block(self, possible_nums, tile):
        left_up_corner = self.BLOCK_SIZE * np.array(
            [tile[0] // self.BLOCK_SIZE, tile[1] // self.BLOCK_SIZE]
        )
        for num in self.board[
            left_up_corner[0] : left_up_corner[0] + self.BLOCK_SIZE,
            left_up_corner[1] : left_up_corner[1] + self.BLOCK_SIZE,
        ].flatten():
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    def get_full_state(self):
        state = {}
        free_tiles = self.__get_free_tiles()
        for ft in free_tiles:
            numbers = copy(self.NUMBERS)
            numbers = self.__check_row(numbers, ft)
            numbers = self.__check_column(numbers, ft)
            numbers = self.__check_block(numbers, ft)
            state[ft] = numbers
        return state

    def get_left_numbers(self):
        numbers_left = []
        for i in self.NUMBERS:
            for _ in range(9 - (self.board == i).sum()):
                numbers_left.append(i)
        return numbers_left

    def __get_left_in_row(self, row_id):
        numbers_left = []
        for i in self.NUMBERS:
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
