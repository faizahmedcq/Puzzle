from reportlab.lib.units import cm
import random
import math


DIFFICULTY_SQUARES = {
    'easy': 40,
    'medium': 70,
    'hard': 90
}


# ==============================
# Sudoku Puzzle Generator
# ==============================
def generate_sudoku_grid(difficulty='easy'):
    """
    Generate a solved Sudoku grid and a puzzle grid with cells removed
    based on the given difficulty.
    Returns:
        (puzzle_grid, solved_grid)
    """
    base = 3
    side = base * base

    def pattern(r, c): 
        return (base * (r % base) + r // base + c) % side

    def shuffle(s): 
        return random.sample(s, len(s))

    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, side + 1))

    solved_board = [[nums[pattern(r, c)] for c in cols] for r in rows]
    puzzle_board = [row[:] for row in solved_board]

    squares_to_remove = DIFFICULTY_SQUARES.get(difficulty, 40)
    for _ in range(squares_to_remove):
        r, c = random.randint(0, 8), random.randint(0, 8)
        puzzle_board[r][c] = ''

    return puzzle_board, solved_board



# ==============================
# Layout Calculation
# ==============================
def get_layout_config(puzzles_per_page, width, height, margin):
    """
    Calculate rows, columns, cell size, and spacing for puzzles per page.
    """
    if puzzles_per_page <= 0:
        puzzles_per_page = 1

    # Predefined layouts
    if puzzles_per_page == 1:
        rows, cols = 1, 1
        
    elif puzzles_per_page == 2:
        rows, cols = 2, 1
    elif puzzles_per_page == 4:
        rows, cols = 2, 2
    elif puzzles_per_page == 6:
        rows, cols = 3, 2
    else:
        cols = math.ceil(math.sqrt(puzzles_per_page))
        rows = math.ceil(puzzles_per_page / cols)

    # Total available width and height for grids
    avail_w = width - 4 * margin
    avail_h = height - 2 * margin

    # Dynamic spacing proportional to available space
    spacing_x = avail_w * 0.02  # 2% of page width
    spacing_y = avail_h * 0.02  # 2% of page height

    # Cell size calculation based on grid and spacing
    cell_w = (avail_w - (cols - 1) * spacing_x) / (9 * cols)
    cell_h = (avail_h - (rows - 1) * spacing_y) / (9 * rows)
    cell_size = min(cell_w, cell_h)

    return rows, cols, cell_size, spacing_x, spacing_y
def draw_puzzle_page(c, puzzles, width, height, margin, cols, rows, cell_size, spacing_x, spacing_y, is_solution=False):
    """
    Draw puzzles or solutions on a single page with dynamic positions.
    """
    total_grid_width = 9 * cell_size * cols + spacing_x * (cols - 1)
    total_grid_height = 9 * cell_size * rows + spacing_y * (rows - 1)

    for idx, puzzle_data in enumerate(puzzles):
        col = idx % cols
        row = idx // cols

        # Compute offsets dynamically
        x_offset = margin + col * (9 * cell_size + spacing_x)
        y_offset = height - margin - row * (9 * cell_size + spacing_y) - 9 * cell_size

        # Draw puzzle title
        title = f"Puzzle {idx+1} {'Solution' if is_solution else puzzle_data['difficulty']} Effort: {puzzle_data['effort']}"
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset, y_offset + 9 * cell_size + 5, title)

        # Choose grid
        grid = puzzle_data['data'][1] if is_solution else puzzle_data['data'][0]

        # Draw the Sudoku grid
        draw_sudoku(c, grid, x_offset, y_offset, 0.8 * cell_size)


def draw_sudoku(c, grid, x_offset, y_offset, cell_size):
    """
    Draws a Sudoku grid on PDF canvas at specified x/y with dynamic cell size.
    """
    y_offset = y_offset - 300
    # Thin lines
    c.setLineWidth(1)
    for i in range(10):
        # Horizontal
        c.line(x_offset, y_offset + i * cell_size, x_offset + 9 * cell_size, y_offset + i * cell_size)
        # Vertical
        c.line(x_offset + i * cell_size, y_offset, x_offset + i * cell_size, y_offset + 9 * cell_size)

    # Thick 3x3 lines
    c.setLineWidth(2)
    for i in range(0, 10, 3):
        # Horizontal
        c.line(x_offset, y_offset + i * cell_size, x_offset + 9 * cell_size, y_offset + i * cell_size)
        # Vertical
        c.line(x_offset + i * cell_size, y_offset, x_offset + i * cell_size, y_offset + 9 * cell_size)
    c.setLineWidth(1)

    # Draw numbers centered in cells
    for r in range(9):
        for c_idx in range(9):
            if grid[r][c_idx]:
                c.drawCentredString(
                    x_offset + c_idx * cell_size + cell_size / 2,
                    y_offset + (8 - r) * cell_size + cell_size / 2 - 2,  # adjust vertical alignment
                    str(grid[r][c_idx])
                )


def draw_title_page(c, width, height):
    """
    Draws a title page for the Sudoku Book.
    """
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height / 2 + 1 * cm, "Sudoku Puzzle Book")
    c.showPage()