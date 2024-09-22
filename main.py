from verification_matrix import *
from solution_finder import *
from transformations import *
from puzzle_generator import *
from puzzle_drawer import *
import datetime

width = 6
height = 6

maximum_repeated_connections = 7

V = generate_verification_matrix(width, height)

puzzle_count = 0
duplicate_checked = 0
solution_checked = 0

search_start = datetime.datetime.now()
seconds_elapsed = 0
while True:
    puzzle_count += 1

    current_time = datetime.datetime.now()
    elapsed = current_time - search_start
    elapsed = elapsed - datetime.timedelta(microseconds=elapsed.microseconds)
    if elapsed.total_seconds() > seconds_elapsed:
        seconds_elapsed = elapsed.total_seconds()
        print(f'{elapsed} - Tested {puzzle_count} puzzles. ', end='')
        print(f'{duplicate_checked} had less than {maximum_repeated_connections} repeated connections, ', end='')
        print(f'{solution_checked} of those had no duplicates.', end='\r')
    T = None
    T_similarity = 1
    while T_similarity > 0:
        T = generate_random_transformation(width, height)
        T_similarity = find_transformation_similarity(V, T)
    p = generate_solvable_puzzle(V, T)
    # Check how many of each connection type there is
    connection_type_count = [[int(s) for s in p[:, 0]].count(i) for i in range(1, max(p[:, 0]))]
    if max(connection_type_count) > maximum_repeated_connections:
        continue

    duplicate_checked += 1

    if has_duplicate_pieces(p):
        continue

    solution_checked += 1

    number = count_solutions(p, width, height)
    if number == 2:
        break
search_end = datetime.datetime.now()

print(f'{elapsed} - Tested {puzzle_count} puzzles. ', end='')
print(f'{duplicate_checked} had less than {maximum_repeated_connections} repeated connections, ', end='')
print(f'{solution_checked} of those had no duplicates.')
print(f'Found a puzzle with only two solutions after {elapsed}')
draw_puzzle(p, width, height, T)
