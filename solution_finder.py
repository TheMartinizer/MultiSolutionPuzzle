from typing import List, Dict, Tuple
import numpy as np


def get_max_repeated_shapes(puzzle: np.array) -> int:
    shape_type_count = [[int(s) for s in puzzle[:, 0]].count(i) for i in range(1, max(puzzle[:, 0]))]
    return max(shape_type_count)


def has_duplicate_pieces(puzzle: np.array) -> bool:
    pieces = []
    for i in range(0, len(puzzle), 4):
        piece = (puzzle[i], puzzle[i + 1], puzzle[i + 2], puzzle[i + 3])
        rotations = [(puzzle[i + j % 4], puzzle[i + (j + 1) % 4], puzzle[i + (j + 2) % 4], puzzle[i + (j + 3) % 4]) for
                     j in range(4)]
        for other_piece in pieces:
            if other_piece in rotations:
                return True
        pieces.append(piece)
    return False


class PuzzlePiece:
    def __init__(self, piece_number: int, connection_shapes: List[int]):
        self.piece_number = piece_number
        self.connection_shapes = connection_shapes

    def get_side_shape(self, side_number: int, rotation_number: int):
        return self.connection_shapes[(side_number - rotation_number) % 4]


class PuzzleSolutionBuilder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.placed_pieces = {}
        self.unfilled_neighbours = {}

    def place_piece(self, piece: PuzzlePiece, rotation: int, position_x: int, position_y: int) -> bool:
        neighbour_restrictions = []
        position = position_y * self.width + position_x

        # Check with neighbours that it fits
        for dx, dy, our_side_facing_neighbour, neighbour_side_facing_us in [(1, 0, 2, 0), (0, 1, 3, 1), (-1, 0, 0, 2),
                                                                            (0, -1, 1, 3)]:
            neighbour_x = position_x + dx
            neighbour_y = position_y + dy
            # Check we're still inside the board
            if (not 0 <= neighbour_x < self.width) or (not 0 <= neighbour_y < self.height):
                # If we're not, our side facing this way must have a shape of zero
                if piece.get_side_shape(our_side_facing_neighbour, rotation) != 0:
                    return False
                continue

            # Check if a neighbouring piece has been placed yet
            neighbour_position = neighbour_y * self.width + neighbour_x
            if neighbour_position in self.placed_pieces:
                # If there is a piece in the neighbouring location, check that this piece is compatible with that
                neighbour_piece, neighbour_rotation = self.placed_pieces[neighbour_position]
                if (
                        neighbour_piece.get_side_shape(neighbour_side_facing_us, neighbour_rotation)
                        + piece.get_side_shape(our_side_facing_neighbour, rotation)
                        != 0
                ):
                    # If we get here, the piece did not fit
                    return False
            else:
                # If there is no neighbour on this side, we should store what shape that neighbour needs to fit
                neighbour_restrictions.append((
                    neighbour_position,
                    neighbour_side_facing_us,
                    -piece.get_side_shape(our_side_facing_neighbour, rotation)
                ))

        # If we went through all the sides, the piece fits. Place it
        self.placed_pieces[position] = (piece, rotation)

        # This is no longer an unfilled neighbour
        if position in self.unfilled_neighbours:
            del self.unfilled_neighbours[position]

        # Add any new unfilled neighbours we found
        for neighbour_position, neighbour_side_facing_us, required_shape in neighbour_restrictions:
            if neighbour_position not in self.unfilled_neighbours:
                self.unfilled_neighbours[neighbour_position] = []
            self.unfilled_neighbours[neighbour_position].append((neighbour_side_facing_us, required_shape))

        return True

    def remove_last_piece(self) -> PuzzlePiece:
        piece_position, (piece, rotation) = self.placed_pieces.popitem()

        requirements_for_replacement_piece = []

        piece_x = piece_position % self.width
        piece_y = piece_position // self.width
        # Update the unfilled neighbours
        for dx, dy, our_side_facing_neighbour, neighbour_side_facing_us in [(1, 0, 2, 0), (0, 1, 3, 1), (-1, 0, 0, 2),
                                                                            (0, -1, 1, 3)]:
            neighbour_x = piece_x + dx
            neighbour_y = piece_y + dy

            # If this side is off the board, we will not need to do anything about any requirements
            if (not 0 <= neighbour_x < self.width) or (not 0 <= neighbour_y < self.height):
                continue

            # If there is still a neighbouring piece on this side, we need to require whichever piece
            # replaces this piece to fit with that neighbour
            neighbour_position = neighbour_y * self.width + neighbour_x
            if neighbour_position in self.placed_pieces:
                requirements_for_replacement_piece.append((
                    our_side_facing_neighbour,
                    piece.get_side_shape(our_side_facing_neighbour, rotation)
                ))
                continue

            # If there is no neighbour on this side, there should be an unfilled neighbour with a set of requirements
            # there. Remove our requirements for that neighbour, and if there are no requirements left, remove the
            # unfilled neighbour completely
            our_requirement = (neighbour_side_facing_us, -piece.get_side_shape(our_side_facing_neighbour, rotation))
            self.unfilled_neighbours[neighbour_position].remove(our_requirement)
            if len(self.unfilled_neighbours[neighbour_position]) == 0:
                del self.unfilled_neighbours[neighbour_position]

        # Leave the requirements for any replacement pieces
        self.unfilled_neighbours[piece_position] = requirements_for_replacement_piece
        return piece

    def get_unfilled_neighbours(self) -> Dict[int, Tuple[int, int]]:
        return self.unfilled_neighbours

    def get_number_of_pieces(self) -> int:
        return len(self.placed_pieces)

    def is_finished(self) -> bool:
        return len(self.placed_pieces) == self.width * self.height


def count_solutions(
        puzzle: np.array,
        width: int,
        height: int
) -> int:
    # Do this in the same way Matt Parker does in the video. Just try every combination of pieces until we find one that
    # works. Keep a running tally of solutions until we are done
    number_of_solutions = 0

    # Create pieces based on the puzzle input
    pieces = []
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            side_shapes = [int(shape) for shape in puzzle[4 * piece_number:4 * piece_number + 4, 0]]
            pieces.append(PuzzlePiece(piece_number, side_shapes))

    # Create a map from a given shape to the pieces that have that shape
    shape_to_pieces_map = {}
    for piece in pieces:
        for side_number in range(4):
            shape = piece.get_side_shape(side_number, 0)
            if shape not in shape_to_pieces_map:
                shape_to_pieces_map[shape] = set()
            shape_to_pieces_map[shape].add((piece, side_number))

    solution_builder = PuzzleSolutionBuilder(width, height)

    # We want to do a depth first search of the puzzle
    # Store it every time we have to make a choice, so we can go back later and do the opposite choice
    available_pieces = set(pieces)
    # Each choice stores which piece to place, its x and y position, rotation, and how many pieces were already
    # laid when making the choice
    choices = [(pieces[0], 0, 0, 0, 0)]
    while len(choices) > 0:
        piece_to_place, position_x, position_y, rotation, pieces_placed_when_making_choice = choices.pop()
        # Since we're doing a depth first search, we only need to remove pieces to get back to the state we were
        # in when we made this choice
        while solution_builder.get_number_of_pieces() > pieces_placed_when_making_choice:
            removed_piece = solution_builder.remove_last_piece()
            # The piece we just removed is available to be placed again
            available_pieces.add(removed_piece)

        # Try to place the piece
        if not solution_builder.place_piece(piece_to_place, rotation, position_x, position_y):
            # If we couldn't place the piece, this is a dead end, and we must return
            continue

        # The piece we placed is no longer available
        available_pieces.remove(piece_to_place)

        # We might have finished building the puzzle now
        if solution_builder.is_finished():
            number_of_solutions += 1
            continue

        # Check what options we have for placing the next puzzle piece
        options = {}
        for neighbour_position in solution_builder.get_unfilled_neighbours():
            requirements = solution_builder.get_unfilled_neighbours()[neighbour_position]
            # To start with, I'll just find all the pieces that fit one of the requirements
            # Maybe we can do more requirement checking later
            required_side, required_shape = requirements[0]

            # Find all pieces with the required shape, and make sure we only consider pieces that are available
            possible_pieces = shape_to_pieces_map[required_shape]

            # Find the possible rotations for each possible piece
            options[neighbour_position] = []
            for possible_piece, side_number in possible_pieces:
                if possible_piece in available_pieces:
                    options[neighbour_position].append((possible_piece, required_side - side_number))

        # Place a piece in the position with the fewest options
        best_position = min(options, key=lambda position: len(options[position]))
        best_position_x = best_position % width
        best_position_y = best_position // width
        # Create a choice for each possible piece
        for piece, rotation in options[best_position]:
            choices.append((piece, best_position_x, best_position_y, rotation, solution_builder.get_number_of_pieces()))
    return number_of_solutions
