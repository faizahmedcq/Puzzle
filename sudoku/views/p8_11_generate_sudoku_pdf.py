import io
import math
import random
from django.http import FileResponse
from django.shortcuts import render
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from .draw_sudoku import draw_sudoku,generate_sudoku_grid,get_layout_config,draw_title_page


# ==============================
# Constants
# ==============================

ROW_GAP_MAP = {
    1: 0.7 * cm,  # extra gap before row 2
    2: 0.7 * cm,  # extra gap before row 3
}


# ==============================
# Drawing Helpers
# ==============================
def draw_puzzle_page(c, puzzles, width, height, margin, cols, rows, cell_size, spacing_x, spacing_y, is_solution=False):
    """
    Draw puzzles or solutions on a single page.
    """
    total_grid_width = (9 * cell_size * cols) + (spacing_x * (cols - 1))
    total_grid_height = (9 * cell_size * rows) + (spacing_y * (rows - 1))

    for idx, puzzle_data in enumerate(puzzles):
        col = idx % cols
        row = idx // cols

        # Calculate extra vertical gap
        extra_gap = sum(gap for r, gap in ROW_GAP_MAP.items() if row >= r)

        x_offset = margin + (width - 2 * margin - total_grid_width) / 2 + col * (9 * cell_size + spacing_x)
        y_offset = height - margin - (height - 2 * margin - total_grid_height) / 2 - row * (9 * cell_size + spacing_y) - extra_gap

        title = f"Puzzle {idx+1} {'Solution' if is_solution else puzzle_data['difficulty']} Effort: {puzzle_data['effort']}"
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x_offset, y_offset, title)

        grid = puzzle_data['data'][1] if is_solution else puzzle_data['data'][0]
        draw_sudoku(c, grid, x_offset, y_offset - 1.5 * cm, cell_size)





# ==============================
# Main PDF Generator View
# ==============================
def generate_sudoku_pdf(request):
    if request.method != 'POST':
        return render(request, 'sudoku/sudoku_generator_form.html')

    # Form data
    easy_count = int(request.POST.get('easy_count'))
    medium_count = int(request.POST.get('medium_count', 30))
    hard_count = int(request.POST.get('hard_count', 20))
    per_page = int(request.POST.get('sudoku_per_page', 6))
    paper_size = request.POST.get('paper_size','page1')
    include_solutions = request.POST.get('include_solutions', 'off') == 'on'

    print("paper_size ,easy_count",paper_size,easy_count)
    # -------------------------------
    # Map layout to page size
    # -------------------------------
    if paper_size == "page1":
        page_size = (8.5 * inch, 11 * inch)  # 8.5 x 11 inches
    elif paper_size == "page2":
        page_size = (6 * inch, 9 * inch)     # 6 x 9 inches
    else:
        page_size = (8.5 * inch, 11 * inch)  # default
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size
    margin = 1.5 * cm
    print("Page Size",page_size)
    # Layout config
    rows, cols, cell_size, spacing_x, spacing_y = get_layout_config(per_page, width, height, margin)

    # Prepare all puzzles
    all_puzzles = []
    for _ in range(easy_count):
        all_puzzles.append({'difficulty': 'Easy', 'data': generate_sudoku_grid('easy'), 'effort': random.randint(100, 200)})
    for _ in range(medium_count):
        all_puzzles.append({'difficulty': 'Medium', 'data': generate_sudoku_grid('medium'), 'effort': random.randint(201, 400)})
    for _ in range(hard_count):
        all_puzzles.append({'difficulty': 'Hard', 'data': generate_sudoku_grid('hard'), 'effort': random.randint(401, 600)})

    # Title page
    draw_title_page(c, width, height)

    # Draw puzzles
    for i in range(0, len(all_puzzles), per_page):
        page_puzzles = all_puzzles[i:i + per_page]
        print('page_puzzles', page_puzzles)
        draw_puzzle_page(c, page_puzzles, width, height, margin, cols, rows, cell_size, spacing_x, spacing_y, per_page)
        c.showPage()

    # Draw solutions
    if include_solutions:
        for i in range(0, len(all_puzzles), per_page):
            page_puzzles = all_puzzles[i:i + per_page]
            draw_puzzle_page(c, page_puzzles, width, height, margin, cols, rows, cell_size, spacing_x, spacing_y, is_solution=True)
            c.showPage()

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="Sudoku_Book.pdf")
