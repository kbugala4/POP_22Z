from copy import deepcopy
import numpy as np


class Sudoku(object):
    NUMBERS = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    BLOCK_SIZE = 3

    def __init__(self, board):
        self.board = board

    def __get_free_tiles(self):
        free_tiles_arrs = np.where(self.board == 0)
        return list(zip(free_tiles_arrs[0], free_tiles_arrs[1]))

    def __get_occupied_tiles(self):
        occ_tiles_arrs = np.where(self.board != 0)
        return list(zip(occ_tiles_arrs[0], occ_tiles_arrs[1]))

    def __check_row(self, possible_nums, tile):
        print(tile)
        print(self.board[tile[0], :])
        print(possible_nums)
        for num in self.board[:, tile[1]]:
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    def __check_column(self, possible_nums, tile):
        for num in self.board[:, tile[1]]:
            if num != 0 and num in possible_nums:
                possible_nums.remove(num)
        return possible_nums

    # def __check_block(self, tile):

    #     for num in self.board[
    #         max(0, tile[0] - self.BLOCK_SIZE) : min(
    #             tile[0] + self.BLOCK_SIZE, len(self.NUMBERS) - 1
    #         ),
    #         max(0, tile[1] - self.BLOCK_SIZE) : min(
    #             tile[1] + self.BLOCK_SIZE, len(self.NUMBERS) - 1
    #         ),
    #     ]:
    #         if num != 0

    def get_full_state(self):
        state = {}
        free_tiles = self.__get_free_tiles()
        for ft in free_tiles:
            numbers = deepcopy(self.NUMBERS)
            numbers = self.__check_row(numbers, ft)
            numbers = self.__check_column(numbers, ft)
            state[ft] = numbers
        return state

    def get_left_numbers(self):
        numbers_left = []
        for i in self.NUMBERS:
            numbers_left.append(i for _ in range(9 - (self.board == i).sum()))
        return numbers_left
