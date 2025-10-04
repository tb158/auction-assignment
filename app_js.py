def get_js():
    return """
    <script>
    // 表示モードの切り替え
    (function(){
      function show(mode){
        var ids=[\"square\",\"fold_rows\",\"fold_cols\"]; ids.forEach(function(id){
          var el=document.getElementById(\"tbl_\"+id); if(!el) return; el.style.display=(id===mode)?\"block\":\"none\";
        });
      }
      document.querySelectorAll(\"input[name='display_mode_html']\").forEach(function(r){ r.addEventListener('change', function(e){ show(e.target.value); }); });
    })();
    
    // 割当操作
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

    function toggleCellColor(i, j) {
        cell_square = document.getElementById("cell-square-" + i + "-" + j)
        row_id = cell_square.getAttribute('row_id');
        col_id = cell_square.getAttribute('col_id');
        // ハイフンの前の数値を取り出す
        let row_id_main = row_id.split('-')[0];
        let col_id_main = col_id.split('-')[0];
        cell_row_fold = document.querySelector(`td[id*="row-fold-"][row_id="${row_id_main}"][col_id="${col_id}"]`);
        cell_column_fold = document.querySelector(`td[id*="column-fold-"][row_id="${row_id}"][col_id="${col_id_main}"]`);
        // console.log(cell_row_fold);
        // console.log(cell_column_fold);
        let value = parseInt(cell_square.getAttribute('data-value'), 10);

        // セルの色をトグル
        if (cell_square.style.backgroundColor === 'orange') {
            if (selectedRows.has(i)) {
                selectedRows.delete(i);
            }
            if (selectedCols.has(j)) {
                selectedCols.delete(j);
            }
            cell_square.style.backgroundColor = originalColors.get(cell_square);
            cell_row_fold.style.backgroundColor = originalColors.get(cell_row_fold);
            cell_column_fold.style.backgroundColor = originalColors.get(cell_column_fold);
            sum -= value;
        } else {
            if (selectedRows.has(i) || selectedCols.has(j)) {
                return;
            }
            selectedRows.add(i);
            selectedCols.add(j);
            originalColors.set(cell_square, cell_square.style.backgroundColor);
            originalColors.set(cell_row_fold, cell_row_fold.style.backgroundColor);
            originalColors.set(cell_column_fold, cell_column_fold.style.backgroundColor);
            cell_square.style.backgroundColor = 'orange';
            cell_row_fold.style.backgroundColor = 'orange';
            cell_column_fold.style.backgroundColor = 'orange';
            sum += value;
        }
        document.getElementById('sum-display').innerText = '割当合計: ' + sum;
    }
    </script>
    """