import numpy as np


def generate_solvable_puzzle(verification_matrix: np.array, transformation_matrix: np.array) -> np.array:
    # Both the verification matrix and the transformation matrix are square matrices, with a number of rows equal to the
    # number of sides in the puzzle
    trial_solution = np.zeros((len(verification_matrix), 1), np.int16)

    # Find each pair of sides that are constrained by each other in the unscrambled puzzle
    constraint_matrices = [verification_matrix, verification_matrix @ transformation_matrix]
    pairs = {}
    for constraint_matrix in constraint_matrices:
        for row in constraint_matrix:
            constrained_sides = []
            for index, value in enumerate(row):
                if value != 0:
                    constrained_sides.append(index)
            # If this side is not constrained by any other, it is an edge piece.
            # We'll ignore it and leave its value at 0
            if len(constrained_sides) != 2:
                continue

            for i in range(2):
                side = constrained_sides[i]
                other_side = constrained_sides[(i + 1) % 2]
                if side not in pairs:
                    pairs[side] = set()
                pairs[side].add(other_side)

    # Pick a side that does not have a set shape, set an arbitrary shape,
    # set all other sides that are constrained by this.
    # Repeat until no unset sides are left
    unset_sides = set(side for side in pairs)
    shape_number = 1

    while len(unset_sides) > 0:
        starting_side = unset_sides.pop()
        trial_solution[starting_side] = shape_number
        shape_number += 1

        affected_sides = [starting_side]
        affected_side_counter = 0
        while affected_side_counter < len(affected_sides):
            current_side = affected_sides[affected_side_counter]
            unset_sides.discard(current_side)
            for other_side in pairs[current_side]:
                trial_solution[other_side] = -trial_solution[current_side]
                if other_side not in affected_sides:
                    affected_sides.append(other_side)

            affected_side_counter += 1

    return trial_solution
