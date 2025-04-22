def get_js():
    return """
    <script>
    let selectedRows = new Set();
    let selectedCols = new Set();
    let sum = 0;
    let originalColors = new Map();

    function resetAssignment() {
        sum = 0;
        selectedRows.clear();
        selectedCols.clear();
        document.querySelectorAll('td').forEach(cell => {
            if (cell.style.backgroundColor === 'orange') {
                cell.style.backgroundColor = originalColors.get(cell);
            }
        });
        document.getElementById('sum-display').innerText = '割当合計: ' + sum;
    }

    function toggleCellColor(cell, i, j) {
        let value = parseInt(cell.getAttribute('data-value'), 10);

        // セルの色をトグル
        if (cell.style.backgroundColor === 'orange') {
            if (selectedRows.has(i)) {
                selectedRows.delete(i);
            }
            if (selectedCols.has(j)) {
                selectedCols.delete(j);
            }
            cell.style.backgroundColor = originalColors.get(cell);
            sum -= value;
        } else {
            if (selectedRows.has(i) || selectedCols.has(j)) {
                return;
            }
            selectedRows.add(i);
            selectedCols.add(j);
            originalColors.set(cell, cell.style.backgroundColor);
            cell.style.backgroundColor = 'orange';
            sum += value;
        }
        document.getElementById('sum-display').innerText = '割当合計: ' + sum;
    }
    </script>
    """