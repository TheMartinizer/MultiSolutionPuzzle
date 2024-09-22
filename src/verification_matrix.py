import numpy as np


def generate_verification_matrix(width: int, height: int) -> np.array:
    number_of_sides = 4*width*height
    # The verification matrix always uses the value of the entry itself, so start with an identity matrix
    verification_matrix = np.identity(number_of_sides, np.int16)

    # Go through each puzzle piece and add its connection to the right and down
    for x in range(width):
        for y in range(height):
            piece_position = y*width + x
            # Don't add right connection if we're in the rightmost row
            if x != width - 1:
                other_piece_position = y*width + x + 1
                right_side_of_left_piece = 4*piece_position + 2
                left_side_of_right_piece = 4*other_piece_position
                verification_matrix[right_side_of_left_piece][left_side_of_right_piece] = 1
                verification_matrix[left_side_of_right_piece][right_side_of_left_piece] = 1
            # Also don't add down connection if we're in the bottom row
            if y != height - 1:
                other_piece_position = (y+1)*width + x
                bottom_side_of_top_piece = 4*piece_position + 3
                top_side_of_bottom_piece = 4*other_piece_position + 1
                verification_matrix[top_side_of_bottom_piece][bottom_side_of_top_piece] = 1
                verification_matrix[bottom_side_of_top_piece][top_side_of_bottom_piece] = 1

    return verification_matrix
