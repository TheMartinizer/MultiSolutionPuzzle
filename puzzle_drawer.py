from ipycanvas import Canvas
from PIL import Image
import numpy as np


def draw_puzzle(puzzle, width, height, scramble=None):
    if scramble is None:
        canvas = Canvas(width=100 * width, height=100 * height, sync_image_data=True)
    else:
        canvas = Canvas(width=200 * width + 50, height=100 * height, sync_image_data=True)

    image = Image.open('matt_and_steve.png')

    # Crop depending on puzzle aspect ratio
    desired_width_pixels = 100 * width
    desired_height_pixels = 100 * height

    width_resize = desired_width_pixels / image.width
    height_resize = desired_height_pixels / image.height

    if height_resize > width_resize:
        image = image.resize((int(height_resize * image.width), int(height_resize * image.height)), Image.LANCZOS)

        left_crop = 110 * height_resize
        if image.width - left_crop < 100 * width:
            left_crop = image.width - 100 * width
        image = image.crop((int(left_crop), 0, int(left_crop) + 100 * width, 100 * height))
    else:
        image = image.resize((int(width_resize * image.width), int(width_resize * image.height)), Image.LANCZOS)

        top_crop = 100 * width_resize
        if image.height - top_crop < 100 * height:
            top_crop = image.height - 100 * height
        image = image.crop((0, int(top_crop), 100 * width, int(top_crop) + 100 * height))

    # Cut image into pieces
    image_pieces = {}
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            image_piece = image.crop((x * 100, y * 100, (x + 1) * 100, (y + 1) * 100))
            image_pieces[piece_number] = image_piece

    # Draw original puzzle
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            image_piece = image_pieces[piece_number]
            canvas.put_image_data(np.asarray(image_piece), x * 100, y * 100)

    # Draw borders between puzzle pieces
    canvas.stroke_style = 'black'
    for x in range(width + 1):
        canvas.stroke_line(x * 100, 0, x * 100, 100 * height)
    for y in range(height + 1):
        canvas.stroke_line(0, y * 100, width * 100, y * 100)

    # Draw piece number at the centre of each piece
    canvas.stroke_style = 'white'
    canvas.text_align = 'center'
    canvas.text_baseline = 'middle'
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            center_x = 100 * x + 50
            center_y = 100 * y + 50
            canvas.stroke_text(str(piece_number), center_x, center_y)

    # Draw shape type at the edge of each piece
    canvas.stroke_style = 'red'
    directions = {
        0: (-42, 0),
        1: (0, -40),
        2: (42, 0),
        3: (0, 40)
    }

    for index, value in enumerate(puzzle[:, 0]):
        if value == 0:
            continue
        piece_number = index // 4
        center_x = 100 * (piece_number % width) + 50
        center_y = 100 * (piece_number // width) + 50

        direction = index % 4
        dx, dy = directions[direction]

        canvas.stroke_text(str(value), center_x + dx, center_y + dy)

    # Draw a dot above each number, to show that pieces are in their original orientation
    canvas.fill_style = 'green'
    for x in range(width):
        for y in range(height):
            location_x = x * 100 + 50
            location_y = y * 100 + 35
            canvas.fill_circle(location_x, location_y, 3)

    # If there is no scramble, we are done now
    if scramble is None:
        return canvas

    # Else, map where each piece has gone to and whether it is rotated
    scramble_map = {}
    for new_piece_number in range(width * height):
        column_set_to_one = min(
            index for index, value in enumerate(scramble[new_piece_number * 4, :]) if value != 0)
        old_piece_number = column_set_to_one // 4
        piece_rotation = column_set_to_one % 4
        scramble_map[new_piece_number] = (old_piece_number, piece_rotation)

    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            old_piece_number, rotation = scramble_map[piece_number]
            image_piece = image_pieces[old_piece_number]
            image_piece = image_piece.rotate(90 * rotation)
            canvas.put_image_data(np.asarray(image_piece), (width + x) * 100 + 50, y * 100)

    # Draw borders between puzzle pieces
    canvas.stroke_style = 'black'
    for x in range(width + 1):
        canvas.stroke_line((x + width) * 100 + 50, 0, (x + width) * 100 + 50, 100 * height)
    for y in range(height + 1):
        canvas.stroke_line(100 * width + 50, y * 100, 200 * width + 50, y * 100)

    # Draw piece numbers of the moved pieces
    canvas.stroke_style = 'white'
    canvas.text_align = 'center'
    canvas.text_baseline = 'middle'
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            old_piece_number, _ = scramble_map[piece_number]

            center_x = 100 * (width + x) + 100
            center_y = 100 * y + 50

            canvas.stroke_text(str(old_piece_number), center_x, center_y)

    # Draw connection shape types on the moved pieces
    canvas.stroke_style = 'red'
    directions = {
        0: (-42, 0),
        1: (0, -40),
        2: (42, 0),
        3: (0, 40)
    }

    for index, value in enumerate((scramble @ puzzle)[:, 0]):
        if value == 0:
            continue
        piece_number = index // 4
        center_x = 100 * (width + piece_number % width) + 100
        center_y = 100 * (piece_number // width) + 50

        direction = index % 4
        dx, dy = directions[direction]

        canvas.stroke_text(str(value), center_x + dx, center_y + dy)

    # Draw green dots to show how each piece has been rotated
    canvas.fill_style = 'green'
    rotations = {
        0: (0, -15),
        1: (-15, 0),
        2: (0, 15),
        3: (15, 0)
    }
    for x in range(width):
        for y in range(height):
            piece_number = y * width + x
            _, rotation = scramble_map[piece_number]

            center_x = 100 * (width + x) + 100
            center_y = 100 * y + 50

            dx, dy = rotations[rotation]
            canvas.fill_circle(center_x + dx, center_y + dy, 3)

    return canvas
