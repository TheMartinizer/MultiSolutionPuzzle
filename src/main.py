from IPython.core.display_functions import display

from verification_matrix import *
from solution_finder import *
from scrambles import *
from puzzle_generator import *
from puzzle_drawer import *
import datetime


width = 5
height = 5
maximum_repeated_shapes = 10

V = generate_verification_matrix(width, height)


def print_progress(elapsed, puzzle_count, duplicate_checked, solution_checked):
    print(f'\r{elapsed} - Tested {puzzle_count} puzzles. ', end='')
    print(f'{duplicate_checked} had {maximum_repeated_shapes} or fewer repetitions of each connection shape, ', end='')
    print(f'{solution_checked} of those had no duplicate pieces.', end='')


# I'm putting the code inside a main function since this makes it easier to profile
def main(max_time=-1):
    puzzle_count = 0
    duplicate_checked = 0
    solution_checked = 0

    search_start = datetime.datetime.now()
    seconds_elapsed = 0

    puzzle_found = None
    scramble_found = None

    while True:
        puzzle_count += 1
        current_time = datetime.datetime.now()
        elapsed = current_time - search_start
        elapsed = elapsed - datetime.timedelta(microseconds=elapsed.microseconds)
        if max_time != -1 and elapsed.total_seconds() > max_time:
            break

        if elapsed.total_seconds() > seconds_elapsed:
            seconds_elapsed = elapsed.total_seconds()
            print_progress(elapsed, puzzle_count, duplicate_checked, solution_checked)

        scramble = None
        scramble_similarity = 1
        while scramble_similarity > 0:
            scramble = generate_random_scramble(width, height)
            scramble_similarity = find_scramble_similarity(V, scramble)
        p = generate_solvable_puzzle(V, scramble)
        # Check how many of each connection type there is

        repeated_shapes = get_number_of_repeated_shapes(p)
        if max(repeated_shapes.values()) > maximum_repeated_shapes:
            continue

        duplicate_checked += 1

        if has_duplicate_pieces(p):
            continue

        solution_checked += 1

        number = count_solutions(p, width, height)
        if number == 2:
            puzzle_found = p
            scramble_found = scramble
            break

    print_progress(elapsed, puzzle_count, duplicate_checked, solution_checked)
    print()
    if puzzle_found is not None:
        print('Found solution with the following puzzle vector: ')
        print(puzzle_found[:,0])
        display(draw_puzzle(puzzle_found, width, height, scramble_found))
    else:
        print('Timed out without finding solution')

    return puzzle_found, scramble_found
best_puzzle, best_scramble = main()