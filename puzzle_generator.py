from typing import Dict, Set
import numpy as np


# Generating a solvable puzzle involves finding the constraints given by a verification matrix and a scramble
# matrix. However, the unscrambled constraints are always the same for a given verification matrix
unscrambled_constraints = {}


def get_constrained_pairs(
        constraint_matrix: np.array,
        existing_pairs: Dict[int, Set[int]] = None
) -> Dict[int, Set[int]]:
    pairs = {}
    # Deep copy the existing pairs, if they exist
    if existing_pairs is not None:
        for side in existing_pairs:
            pairs[side] = set(existing_pairs[side])

    for row in constraint_matrix:
        constrained_sides = np.nonzero(row)[0]
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
    return pairs


def generate_solvable_puzzle(verification_matrix: np.array, scramble_matrix: np.array) -> np.array:
    # Both the verification matrix and the scramble matrix are square matrices, with a number of rows equal to the
    # number of sides in the puzzle
    trial_solution = np.zeros((len(verification_matrix), 1), np.int16)

    # Find each pair of sides that are constrained by each other in the unscrambled puzzle
    pairs = unscrambled_constraints.get(id(verification_matrix), None)
    if pairs is None:
        pairs = get_constrained_pairs(verification_matrix)
        unscrambled_constraints[id(verification_matrix)] = pairs

    pairs = get_constrained_pairs(verification_matrix @ scramble_matrix, pairs)

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
