from collections import Counter

import numpy as np
import matplotlib
matplotlib.use("agg")    # must select backend before importing pyplot
import matplotlib.pyplot as plt
from dimod import BinaryQuadraticModel
from dwave.system import LeapHybridSampler

from exact_cover import exact_cover_bqm

def build_subsets(n):
    
    subsets = []
    for x in range(n):
        for y in range(n):
            col = x
            row = y + n

            subset = {col, row}

            diag = x + y + (2*n - 1)
            min_diag = 2*n
            max_diag = 4*n - 4

            if diag >= min_diag and diag <= max_diag:
                subset.add(diag)

            anti_diag = (n - 1 - x + y) + (4*n - 4)
            min_anti_diag = 4*n - 3
            max_anti_diag = 6*n - 7

            if anti_diag >= min_anti_diag and anti_diag <= max_anti_diag:
                subset.add(anti_diag)

            subsets.append(subset)

    return subsets

def handle_diag_constraints(bqm, subsets, diag_constraints):
    
    for constraint in diag_constraints:
        for i in range(len(subsets)):
            if constraint in subsets[i]:
                for j in range(i):
                    if constraint in subsets[j]:
                        bqm.add_interaction(i, j, 2) #penalize duplicates
    return bqm

def n_queens(n, sampler=None):
    
    num_row_col_constraints = 2 * n
    row_col_constraint_ids = set(range(num_row_col_constraints))

    num_diag_constraints = 4 * n - 6   
    diag_constraint_ids = set(range(num_row_col_constraints, num_row_col_constraints + num_diag_constraints))

    
    subsets = build_subsets(n)

    bqm = exact_cover_bqm(row_col_constraint_ids, subsets)

    bqm = handle_diag_constraints(bqm, subsets, diag_constraint_ids) 

    if sampler is None:
        sampler = LeapHybridSampler()

    sampleset = sampler.sample(bqm, label='Example - N Queens')
    sample = sampleset.first.sample  
    
    return [subsets[i] for i in sample if sample[i]]

def is_valid_solution(n, solution):
    
    count = Counter()

    for queen in solution:
        count = count + Counter(queen)

    # Check row/col constraints
    for i in range(2*n):
        if count[i] != 1:
            if i < n:
                col = i
                print("Column {} has {} queens.".format(col, count[i]))
            else:
                row = np.abs(i - (2*n - 1)) # Convert constraint id to row index
                print("Row {} has {} queens.".format(row, count[i]))

            return False

    # Check diag/anti-diag constraints
    for i in range(2*n, 6*n - 6):
        if count[i] > 1:
            if i <= 4*n - 4:
                print("Top-left to bottom-right diagonal {} has {} queens.".format(i, count[i]))
            else:
                print("Bottom-left to top-right diagonal {} has {} queens.".format(i, count[i]))

            return False

    return True

def plot_chessboard(n, queens):
    
    chessboard = np.zeros((n,n))
    chessboard[1::2,0::2] = 1
    chessboard[0::2,1::2] = 1

    # Adjust fontsize for readability
    if n <= 10:
        fontsize = 30
    elif n <= 20:
        fontsize = 10
    else:
        fontsize = 5

    plt.xticks(np.arange(n))
    plt.yticks(np.arange(n))

    plt.imshow(chessboard, cmap='binary')

    # Place queens
    for subset in solution:
        x = y = -1
        for constraint in subset:
            if constraint < n:
                x = constraint
            elif constraint >= n and constraint < 2*n:
                y = np.abs(constraint - (2*n - 1)) # Convert constraint ID to row index

        if x != -1 and y != -1:
            plt.text(x, y, u"\u2655", fontsize=fontsize, ha='center',
                     va='center', color='black' if (x - y) % 2 == 0 else 'white')

    # Save file in root directory
    file_name = "{}-queens-solution.png".format(n)
    plt.savefig(file_name)

    return file_name

def get_sanitized_input():
    while True:
        print("Enter the number of queens to place (n > 0):")
        n = input()

        try:
            n = int(n)
            if n <= 0:
                print("Input must be greater than 0.")
                continue
            if n >= 200:
                # Run but give a warning
                print("Problems with large n will run very slowly.")

        except ValueError:
            print("Input type must be int.")
            continue

        return n

if __name__ == "__main__":
    n = get_sanitized_input()

    if n > 20:
        print("Solution image is large and may be difficult to view.")
        print("Plot settings in plot_chessboard() may need adjusting.")

    print("Trying to place {n} queens on a {n}*{n} chessboard.".format(n=n))
    solution = n_queens(n)

    if is_valid_solution(n, solution):
        print("Solution is valid.")
    else:
        print("Solution is invalid.")

    file_name = plot_chessboard(n, solution)
    print("Chessboard created. See: {}".format(file_name))
