from typing import Tuple
import numpy as np
import random


def categorize_position(width: int, height: int, x: int, y: int) -> Tuple[str, int]:
    if y == 0:
        if x == 0:
            return 'corner', 0
        elif x == width - 1:
            return 'corner', 3
        else:
            return 'edge', 0
    elif y == height - 1:
        if x == 0:
            return 'corner', 1
        elif x == width - 1:
            return 'corner', 2
        else:
            return 'edge', 2
    elif x == 0:
        return 'edge', 1
    elif x == width - 1:
        return 'edge', 3
    else:
        return 'middle', 0


# Store already calculated rotation matrices, to save on computation
rotation_matrices = {}


def generate_random_scramble(width: int, height: int) -> np.array:
    number_of_sides = 4 * width * height
    scramble = np.zeros((number_of_sides, number_of_sides), np.int16)

    # Group pieces in corners, edges and middle, shuffle them, and then fill them in using the shuffled order
    corners = []
    edges = []
    middles = []
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            category, _ = categorize_position(width, height, x, y)
            if category == 'corner':
                corners.append(piece_number)
            elif category == 'edge':
                edges.append(piece_number)
            elif category == 'middle':
                middles.append(piece_number)

    random.shuffle(corners)
    random.shuffle(edges)
    random.shuffle(middles)

    # Now fill in the puzzle
    for scrambled_x in range(width):
        for scrambled_y in range(height):
            category, orientation = categorize_position(width, height, scrambled_x, scrambled_y)
            if category == 'corner':
                piece_number = corners.pop()
            elif category == 'edge':
                piece_number = edges.pop()
            else:
                piece_number = middles.pop()

            original_x = piece_number % width
            original_y = piece_number // width
            _, original_orientation = categorize_position(width, height, original_x, original_y)
            rotation = (orientation - original_orientation) % 4

            # If the piece is a middle piece, we can rotate it freely
            if category == 'middle':
                rotation = random.randrange(4)

            rotation_matrix = rotation_matrices.get(rotation, None)
            if rotation_matrix is None:
                # Generate a rotation matrix, and place it in the correct position in the larger scramble matrix
                # Each rotation is counter-clockwise and 90 degrees. We can achieve this by shifting each row
                # in the identity matrix one up
                rotation_matrix = np.roll(np.identity(4, np.int16), -rotation, 0)
                rotation_matrices[rotation] = rotation_matrix

            # Place the rotation matrix in the correct spot in the larger scramble matrix
            new_piece_number = scrambled_y * width + scrambled_x
            scramble[
                4 * new_piece_number:4 * new_piece_number + 4,
                4 * piece_number:4 * piece_number + 4
            ] = rotation_matrix

    return scramble


# Store pre-generated unique puzzles. This saves quite a lot of execution time
generated_puzzles = {}


def get_unique_puzzle(verification_matrix: np.array) -> np.array:
    unique_puzzle, number_of_edges = generated_puzzles.get(id(verification_matrix), (None, None))

    if unique_puzzle is None:
        # Generate a puzzle where each connection is unique
        unique_puzzle = np.zeros((len(verification_matrix), 1), np.int16)
        number_of_edges = 0
        shape_number = 1
        for row in verification_matrix:
            connected_sides = []
            for index, value in enumerate(row):
                if value != 0:
                    connected_sides.append(index)
            if len(connected_sides) == 1:
                number_of_edges += 1
            else:
                unique_puzzle[connected_sides[0]] = shape_number
                unique_puzzle[connected_sides[1]] = -shape_number
                shape_number += 1
        generated_puzzles[id(verification_matrix)] = (unique_puzzle, number_of_edges)
    return unique_puzzle, number_of_edges


def find_scramble_similarity(verification_matrix: np.array, scramble_matrix: np.array) -> int:
    # The unique_puzzle is a puzzle where the shapes of every connection is unique
    unique_puzzle, number_of_edges = get_unique_puzzle(verification_matrix)
    # Now, the number of sides that are still touching in the scrambled puzzle is equal to the number of zeros in the
    # vector generated by the verification matrix, minus the number of edges (which are always zero in the vector)
    verification_vector = verification_matrix @ scramble_matrix @ unique_puzzle
    similarity = -number_of_edges
    for entry in verification_vector:
        if entry == 0:
            similarity += 1
    # Each similarity is counted twice in the verification vector
    return similarity // 2
