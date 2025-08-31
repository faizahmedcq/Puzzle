// Get references
const checkboxes = document.querySelectorAll('input[type="checkbox"]');
const inputs = document.querySelectorAll('input[type="number"]');
const selectedText = document.getElementById('selected-text');

function updateSelectedText() {
    const categories = ['Easy', 'Medium', 'Hard'];
    let parts = [];

    categories.forEach((category, index) => {
        const checkbox = checkboxes[index];
        const input = inputs[index];
        const value = parseInt(input.value) || 0; // ensure numeric
        if (checkbox.checked && value > 0) {
            parts.push(`${value} ${category}`);
        }
    });

    selectedText.textContent = parts.length > 0 ? `Selected: ${parts.join(', ')}` : 'Selected: None';
}

// Event listeners
checkboxes.forEach(cb => cb.addEventListener('change', updateSelectedText));
inputs.forEach(input => input.addEventListener('input', updateSelectedText));

// Initialize on page load
updateSelectedText();