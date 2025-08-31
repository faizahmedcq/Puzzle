document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pdfPreviewCanvas');
    const ctx = canvas.getContext('2d');

    // Page settings (match Python page size & margins)
    const pageWidth = canvas.width;
    const pageHeight = canvas.height;
    const margin = 40;

    // Grid settings
    const cellSize = 20;       // pixels
    const gridSpacing = 10;    // spacing between grids
    const perPage = 6;         // number of puzzles per page
    const rows = 2;
    const cols = 3;

    // Sample puzzle data (you can dynamically fetch via AJAX)
    const samplePuzzles = [
        ['4', '', '8', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', '', ''],
    ];

    function drawSudokuGrid(xOffset, yOffset, grid) {
        const smallCell = cellSize;
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 1;

        // Draw 9x9 grid
        for (let r = 0; r < 9; r++) {
            for (let c = 0; c < 9; c++) {
                ctx.strokeRect(
                    xOffset + c * smallCell,
                    yOffset + r * smallCell,
                    smallCell,
                    smallCell
                );
                const val = grid[r][c];
                if (val) {
                    ctx.fillStyle = 'black';
                    ctx.font = `${smallCell * 0.6}px Arial`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(val, xOffset + c * smallCell + smallCell/2, yOffset + r * smallCell + smallCell/2);
                }
            }
        }

        // Draw thick 3x3 borders
        ctx.lineWidth = 2;
        for (let i = 0; i <= 9; i += 3) {
            ctx.beginPath();
            // vertical
            ctx.moveTo(xOffset + i * smallCell, yOffset);
            ctx.lineTo(xOffset + i * smallCell, yOffset + 9 * smallCell);
            ctx.stroke();
            // horizontal
            ctx.moveTo(xOffset, yOffset + i * smallCell);
            ctx.lineTo(xOffset + 9 * smallCell, yOffset + i * smallCell);
            ctx.stroke();
        }
    }

    function drawPage() {
        let count = 0;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const x = margin + c * (9 * cellSize + gridSpacing);
                const y = margin + r * (9 * cellSize + gridSpacing);
                drawSudokuGrid(x, y, samplePuzzles);
                count++;
                if (count >= perPage) return;
            }
        }
    }

    drawPage();
});