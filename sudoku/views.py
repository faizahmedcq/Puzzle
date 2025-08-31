import io
import random
from django.http import FileResponse
from django.shortcuts import render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm
import math

# Create your views here.

def sudoku(request):
    """
    Renders the main Sudoku form page.
    """
    return render(request, 'sudoku/home_sudoku.html')

def generate_sudoku_grid(difficulty='easy'):
    """
    Generates a full Sudoku solution and a puzzle grid based on difficulty.
    """
    base = 3
    side = base * base

    # pattern for a baseline valid solution
    def pattern(r, c): return (base * (r % base) + r // base + c) % side
    def shuffle(s): return random.sample(s, len(s))
    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, side + 1))

    # A fully solved board
    solved_board = [[nums[pattern(r, c)] for c in cols] for r in rows]

    # Create a copy for the puzzle board
    puzzle_board = [row[:] for row in solved_board]

    # Change made here: Increased squares to remove for 'hard' difficulty
    squares_to_remove = {'easy': 40, 'medium': 50, 'hard': 60}
    for _ in range(squares_to_remove.get(difficulty, 40)):
        r = random.randint(0, 8)
        c = random.randint(0, 8)
        puzzle_board[r][c] = ''
    
    return puzzle_board, solved_board

# Function to draw a Sudoku grid on PDF
def draw_sudoku(c, grid, x_offset, y_offset, cell_size=1*cm):
    """
    Draws a Sudoku grid on the PDF canvas with correctly aligned thick 3x3 lines.
    """
    x_offset = x_offset+5
    y_offset = y_offset+50
    # Draw thin lines for the grid
    c.setLineWidth(1)
    for i in range(10):  # Horizontal lines
        c.line(x_offset, y_offset - i * cell_size, x_offset + 9 * cell_size, y_offset - i * cell_size)
    for j in range(10):  # Vertical lines
        c.line(x_offset + j * cell_size, y_offset, x_offset + j * cell_size, y_offset - 9 * cell_size)

    # Draw thicker lines for 3x3 blocks
    c.setLineWidth(2)
    for i in range(0, 10, 3):  # Horizontal thick lines
        c.line(x_offset, y_offset - i * cell_size, x_offset + 9 * cell_size, y_offset - i * cell_size)
    for j in range(0, 10, 3):  # Vertical thick lines
        c.line(x_offset + j * cell_size, y_offset, x_offset + j * cell_size, y_offset - 9 * cell_size)
    c.setLineWidth(1)

    # Draw numbers centered in cells
    for i in range(9):
        for j in range(9):
            if grid[i][j]:
                c.drawCentredString(
                    x_offset + j * cell_size + cell_size / 2,
                    y_offset - i * cell_size - cell_size / 2 + 4,  # vertical adjust
                    str(grid[i][j])
                )

def get_layout_config(puzzles_per_page, width, height, margin):
    """
    Dynamically calculates the layout configuration (rows, columns, cell size, spacing)
    based on the number of puzzles per page.
    """
    if puzzles_per_page <= 0:
        puzzles_per_page = 1
    
    # Standard grid layouts for common numbers of puzzles
    if puzzles_per_page == 1:
        rows, cols = 1, 1
    elif puzzles_per_page == 2:
        rows, cols = 2, 1
    elif puzzles_per_page == 4:
        rows, cols = 2, 2
    elif puzzles_per_page == 6:
        rows, cols = 3, 2  # Adjusted for a cleaner 2-puzzle-per-row layout
    else:
        # Generic calculation for other numbers
        cols = math.ceil(math.sqrt(puzzles_per_page))
        rows = math.ceil(puzzles_per_page / cols)

    # Set specific horizontal and vertical gaps
    # Increased horizontal gap and decreased vertical gap
    puzzle_spacing_x = 2.0 * cm 
    puzzle_spacing_y = 0.5 * cm
    
    available_width = width - 2 * margin
    available_height = height - 2 * margin
    
    # Calculate cell size based on width and height and take the smaller one
    cell_size_w = (available_width - (cols - 1) * puzzle_spacing_x) / (9 * cols)
    cell_size_h = (available_height - (rows - 1) * puzzle_spacing_y) / (9 * rows)
    cell_size = min(cell_size_w, cell_size_h)
    
    return rows, cols, cell_size, puzzle_spacing_x, puzzle_spacing_y


def generate_sudoku_pdf(request):
    """
    View to handle form submission and generate the Sudoku book PDF.
    """
    if request.method != 'POST':
        return render(request, 'sudoku/sudoku_generator_form.html')

    # Get form data, using .get() with a default value to prevent errors
    easy_count = int(request.POST.get('easy_count', 50))
    medium_count = int(request.POST.get('medium_count', 30))
    hard_count = int(request.POST.get('hard_count', 20))
    puzzles_per_page = int(request.POST.get('sudoku_per_page', 6))
    paper_size_name = request.POST.get('paper_size', 'a4')
    author_name = request.POST.get('author_name', 'John Doe')
    include_solutions = request.POST.get('include_solutions', 'off') == 'on'

    # Choose page size
    if paper_size_name == 'us_letter':
        page_size = letter
    else:
        page_size = A4

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size
    margin = 1.5*cm

    # Dynamically get layout configuration
    rows, cols, cell_size, puzzle_spacing_x, puzzle_spacing_y = get_layout_config(puzzles_per_page, width, height, margin)
    
    # Store all puzzles and their original difficulties
    all_puzzles = []
    for _ in range(easy_count):
        all_puzzles.append({'difficulty': 'Easy', 'data': generate_sudoku_grid('easy'), 'effort': random.randint(100,200)})
    for _ in range(medium_count):
        all_puzzles.append({'difficulty': 'Medium', 'data': generate_sudoku_grid('medium'), 'effort': random.randint(201,400)})
    for _ in range(hard_count):
        all_puzzles.append({'difficulty': 'Hard', 'data': generate_sudoku_grid('hard'), 'effort': random.randint(401,600)})

    random.shuffle(all_puzzles)

    def draw_header_footer(c, page_number, title, is_solutions=False):
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - margin, title)
        c.setFont("Helvetica", 10)
        c.drawRightString(width - margin, margin, f"Page {page_number}")
        if is_solutions:
            c.setFont("Helvetica", 12)
            c.drawCentredString(width / 2, height - margin - 0.5*cm, "Solutions")
    
    # The first page will be a title page
    c.setFont("Helvetica-Bold", 20)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height / 2 - 1*cm, f"By {author_name}")
    c.showPage()
    
    page_number = 1
    puzzles_on_page = 0
    y_start_offset = height - margin - 1*cm

    # --- Draw the Puzzles Section ---
    for i, puzzle_data in enumerate(all_puzzles):
        # Check for new page
        if puzzles_on_page >= puzzles_per_page:
            c.showPage()
            puzzles_on_page = 0
            page_number += 1

        
        # Determine puzzle position (row and column)
        col_index = puzzles_on_page % cols
        row_index = puzzles_on_page // cols
        
        # Calculate x and y offsets to center the puzzles
        total_grid_width = (9 * cell_size * cols) + (puzzle_spacing_x * (cols - 1))
        total_grid_height = (9 * cell_size * rows) + (puzzle_spacing_y * (rows - 1))
        
        x_offset = margin + (width - 2 * margin - total_grid_width) / 2 + (col_index * (9 * cell_size + puzzle_spacing_x))
        y_offset = height - margin - (height - 2 * margin - total_grid_height) / 2 - (row_index * (9 * cell_size + puzzle_spacing_y))
        
        # Draw puzzle header
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset, y_offset, f"L-{i+1}-{i+1} {puzzle_data['difficulty']} Effort: {puzzle_data['effort']}")

        # Draw the puzzle grid
        draw_sudoku(c, puzzle_data['data'][0], x_offset, y_offset - 0.5*cm, cell_size)
        
        puzzles_on_page += 1
        
    # --- Draw the Solutions Section ---
    if include_solutions:
        c.showPage()
        page_number += 1
        puzzles_on_page = 0
        
        for i, puzzle_data in enumerate(all_puzzles):
            if puzzles_on_page >= puzzles_per_page:
                c.showPage()
                puzzles_on_page = 0
                page_number += 1


            col_index = puzzles_on_page % cols
            row_index = puzzles_on_page // cols
            
            x_offset = margin + (width - 2 * margin - total_grid_width) / 2 + (col_index * (9 * cell_size + puzzle_spacing_x))
            y_offset = height - margin - (height - 2 * margin - total_grid_height) / 2 - (row_index * (9 * cell_size + puzzle_spacing_y))


            c.setFont("Helvetica-Bold", 10)
            c.drawString(x_offset, y_offset, f"Puzzle {i+1} Solution")

            draw_sudoku(c, puzzle_data['data'][1], x_offset, y_offset - 0.5*cm, cell_size)

            puzzles_on_page += 1

    c.save()
    buffer.seek(0)
    print("PDF generation successful!")
    book_title="sudoku"
    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f'{book_title.replace(" ", "_")}_Sudoku_Book.pdf'
    )