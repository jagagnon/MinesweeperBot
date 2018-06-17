# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

# http://minesweeperonline.com/#beginner-200
# https://github.com/Ghostkeeper/MinesweeperSolver/blob/master/minesweeper.py
# https://github.com/KrisNguyen135/pyautogui-demo/blob/master/mine_sweeper.py
# https://github.com/Scalv/MineSweeperBot/blob/master/Board.py

import pyautogui
import os
import numpy as np
import time
import random

os.chdir('/Users/julien/Dropbox/Python/Minesweeper')

# global game variables
cell_size = 32
anchor_offset = 14  # offset to top left cell corner
vertical_cells = 9
horizontal_cells = 9
num_mines = 10

pyautogui.PAUSE = 0.01

# for each number, this is the rgb coding
value_colours = {
        0: [255, 255, 255],  # unknown
        1: [70, 0, 255],
        2: [0, 131, 7],
        3: [255, 0, 0],
        4: [29, 0, 125],
        5: [136, 0, 0],
        6: [0, 127, 125],
        7: [192, 192, 192],  # don't hvae
        8: [0, 0, 0],  # TBD
        9: [189, 189, 189],  # empty
        99: [99, 99, 99],  # fmnual recoding
        98: [0, 0, 0]  # mine
}

# sum the rgb dimensions to reverse map
sum_colours_dict = {sum(v): k for (k, v) in value_colours.items()}


def start_game():
    '''initiate minesweeper bot and board and select first cell'''
    anchor = pyautogui.locateOnScreen('top left anchor.png')
    x_start = anchor[0] + anchor_offset
    y_start = anchor[1] + anchor_offset
    pyautogui.click(anchor[0], anchor[1])
    play(x_start, y_start)


def play(x_start, y_start):
    '''main function for bot, loop until a mine is detected or win'''
    # click a random cell to start
    start_cell = []
    start_cell.append((np.random.randint(0, 8), np.random.randint(0, 8)))
    click_cells(x_start, y_start, start_cell)
    detected_mines = False
    mines = 0
    screenshots = 0
    while not detected_mines:
        updated_board = refresh_board(horizontal_cells, vertical_cells,
                                      x_start, y_start)
        screenshots += 1
        print(updated_board, '\n')
        if updated_board[updated_board == 98].any():
            detected_mines = True
            print('Game over motherfucker', '\n n_screeshots:', screenshots)

        else:
            cell_mine, cell_empty = sweep_mines(updated_board)

            # delete empty cells as unflagged mine will still trigger win,
            # while all flagged mines and some unknown cells won't
            if len(cell_empty) > 0:
                click_cells(x_start, y_start, cell_empty)

            # if all mines are detected, clear out remaining empty cells, then
            # break loop, else flag new mines. winning flags remaining mines
            mines += len(cell_mine)
            if mines == num_mines:
                empty_cells = final_cells(updated_board, cell_mine, cell_empty)
                click_cells(x_start, y_start, empty_cells)
                print('Winner, winner, chicken dinner!', '\n n_screeshots:',
                      screenshots)
                break
            else:
                if len(cell_mine) > 0:
                    flag_cells(x_start, y_start, cell_mine)

            # if no moves suggested, click at random
            if len(cell_mine) + len(cell_empty) == 0:
                unknown_cells = free_moves(updated_board)
                x = np.random.randint(0, len(unknown_cells))
                rand_move = []
                rand_move.append(unknown_cells[x])
                click_cells(x_start, y_start, rand_move)


def free_moves(board):
    '''determine which cells are free, need to transform board to match
    orientation on the screen'''
    free_cells = []
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if board[i, j] == 0:
                free_cells.append((i, j))
    return(free_cells)


def final_cells(board, coord_mines, coord_empty):
    '''locate the final empty cells in the board'''
    temp_board = board.copy()
    for coord in coord_mines:
        temp_board[coord[0], coord[1]] = 99
    for coord in coord_empty:
        temp_board[coord[0], coord[1]] = 9
    # * unpacks each of its elements as a seperate argument, allowing tuples
    empty_cells = list(zip(*np.where(temp_board == 0)))
    return(empty_cells)


def click_cells(left, top, list_cells):
    '''click cells in a list of cells passed as an argument'''
    list_cells = sorted(list_cells)
    for cell in list_cells:
        x = left + cell_size * (cell[1] + 0.5)
        y = top + cell_size * (cell[0] + 0.5)
        pyautogui.click(x, y)
        time.sleep(random.randrange(1, 10)/100)


def flag_cells(left, top, list_cells):
    '''flag cells in a list of cells passed as an argument'''
    for cell in list_cells:
        x = left + cell_size * (cell[1] + 0.5)
        y = top + cell_size * (cell[0] + 0.5)
        pyautogui.rightClick(x, y)
        time.sleep(random.randrange(1, 10)/100)


def refresh_board(n_horizontal, n_vertical, left, top):
    '''Generate a board and the cell ids by taking a new screenshot
    and identifying the numbers'''

    # generate a board to update with every new screenshot
    board = np.zeros([n_horizontal, n_vertical])

    # capture a screenshot of the new board
    screenshot = pyautogui.screenshot()

    for i in range(horizontal_cells):
        for j in range(vertical_cells):
            x = left + cell_size * (i + 0.5)
            y = top + cell_size * (j + 0.5)
            num = assign_number(screenshot, x, y)
            board[i, j] = num
    return(board.T)


def assign_number(im, x, y):
    '''for each cell in the screenshot, assign a value based on a dictionary
    of RGB colours for each number'''
    r, g, b = im.getpixel((x, y))[0:3]
    # to differentiate between empty and unknown cells
    if r == 189:
        r, g, b = im.getpixel((x - cell_size//2 + 2, y))[0:3]
    # to differentiate between mines and flagged cells, sample upwards 5px
    elif r == 0:
        r2, g2, b2 = im.getpixel((x, y-5))[0:3]
        if r2 == 255:
            r, g, b = 99, 99, 99
    sum_colour = r + g + b
    # recode for borderline colour sampling inaccuracies (pick better start pt)
    if sum_colour == 569 or sum_colour == 369:
        sum_colour = 765
    value = sum_colours_dict[sum_colour]
    return(value)


def sweep_mines(board):
    '''for each row in the board, sweep around numbers and flag mines and
    tiles to click'''
    xy_mines = []
    xy_del = []
    interim_board = board.copy()
    for i in range(interim_board.shape[0]):
        cols = np.where(np.isin(interim_board[i], range(1, 9)))[0]
        if len(cols) > 0:
            for j in cols:
                coord_mines, coord_del = flag_mines(interim_board, i, j)
                xy_mines += coord_mines
                xy_del += coord_del
                interim_board = sweep_interim_board(interim_board, coord_mines)
    xy_del = list(set(xy_del))
    print(' mines: ', xy_mines, '\n empty: ', xy_del)
    return(xy_mines, xy_del)


def sweep_interim_board(board, coord_mines):
    '''update board in between screenshots with found mines'''
    for xy in coord_mines:
        board[xy[0], xy[1]] = 99
    return(board)


def flag_mines(board, i, j):
    '''generate a list of coordinates of mines and cells to delete'''

    # understand what is around the cell in question
    neighbour_cells, neighbour_coords = sweep_surroundings(board, i, j)
    cell_value = board[i, j]

    # empty lists unless otherwise specified
    coord_mines = []
    coord_del = []
    neighbour_cells = np.array(neighbour_cells)
    n_unknown = np.sum(neighbour_cells == 0)
    n_flagged = np.sum(neighbour_cells == 99)

    # if there are any unknown cells in the neighouring cells
    if n_unknown > 0:

        # if all mines have been identified, flag remaining cells for deletion
        if cell_value == n_flagged:
            index = np.where(neighbour_cells == 0)[0]
            for x in index:
                coord_del.append(neighbour_coords[x])

        # if all mines have been identified, flag remaining cells for deletion
        elif cell_value == 1 and cell_value == n_unknown:
            index = np.where(neighbour_cells == 0)[0]
            for x in index:
                coord_mines.append(neighbour_coords[x])

        # determine if all remaining blank cells are mines
        elif cell_value > 1 and cell_value == (n_unknown + n_flagged):
            index = np.where(neighbour_cells == 0)[0]
            for x in index:
                coord_mines.append(neighbour_coords[x])

#    print('coord :', i, ',', j, '\n value:', cell_value, '\n',
#          neighbour_cells, '\n', neighbour_coords, '\n', coord_mines, '\n',
#          coord_del)

    return(coord_mines, coord_del)


def sweep_surroundings(board, i, j):
    '''sweep cells around a number'''
    neighbour_cells = []
    neighbour_coords = []

    # all but top left corner
    if (i > 0) and (j > 0):
        neighbour_cells.append(board[i - 1, j - 1])
        neighbour_coords.append((i - 1, j - 1))
    # all but top row
    if (i > 0):
        neighbour_cells.append(board[i - 1, j])
        neighbour_coords.append((i - 1, j))
    # all but top right corner
    if (i > 0) and (j < horizontal_cells - 1):
        neighbour_cells.append(board[i - 1, j + 1])
        neighbour_coords.append((i - 1, j + 1))
    # all but rightmost column
    if (j < horizontal_cells - 1):
        neighbour_cells.append(board[i, j + 1])
        neighbour_coords.append((i, j + 1))
    # all but bottom right corner
    if (i < vertical_cells - 1) and (j < horizontal_cells - 1):
        neighbour_cells.append(board[i + 1, j + 1])
        neighbour_coords.append((i + 1, j + 1))
    # all but bottom row
    if (i < vertical_cells - 1):
        neighbour_cells.append(board[i + 1, j])
        neighbour_coords.append((i + 1, j))
    # all but bottom left corner
    if (i < vertical_cells - 1) and (j > 0):
        neighbour_cells.append(board[i + 1, j - 1])
        neighbour_coords.append((i + 1, j - 1))
    # all but leftmost column
    if (j > 0):
        neighbour_cells.append(board[i, j - 1])
        neighbour_coords.append((i, j - 1))

    return(neighbour_cells, neighbour_coords)
