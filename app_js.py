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
    let lastAssignmentCount = 0;
    
    // 割当結果を管理する配列（座標形式）
    let AssignmentsForRowFold = []; // 配列 of assigned coordinates [row_id, col_id_main]
    let AssignmentsForColumnFold = []; // 配列 of assigned coordinates [row_id, col_id_main]
    
    // ページ読み込み完了後に初期割当を適用
    applyInitialAssignments();
    // document.addEventListener('DOMContentLoaded', applyInitialAssignments);
    
    // 初期割当の適用（割当ボタンが押されるたびに実行）
    function applyInitialAssignments() {
        const tblSquare = document.getElementById('tbl_square');
        if (tblSquare && tblSquare.dataset.assignments) {
            try {
                
                // まずオレンジ色をリセット
                resetAssignment();
                
                const assignments = JSON.parse(tblSquare.dataset.assignments);
                if (assignments && assignments.length > 0) {
                    // 少し遅延させてDOMが完全に構築されるのを待つ
                    setTimeout(function() {
                        assignments.forEach(function(assignment) {
                            if (assignment && assignment.length === 2) {
                                toggleCellColor(assignment[0], assignment[1]);
                            }
                        });
                    }, 100);
                }
                
            } catch (e) {
                console.error('Error parsing assignments:', e);
            }
        }
    }
    
    // 割当リセット関数
    function resetAssignment() {
        sum = 0;
        selectedRows.clear();
        selectedCols.clear();
        AssignmentsForRowFold = [];
        AssignmentsForColumnFold = [];
        
        document.querySelectorAll('td').forEach(cell => {
            if (cell.style.backgroundColor === 'orange') {
                cell.style.backgroundColor = originalColors.get(cell);
            }
        });
        
        // 割当結果を更新するメソッドを呼び出す
        updateAssignmentDisplays();
        
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
            
            // 座標形式で割当結果を削除
            const coordinateRowFold = [row_id_main, j];
            const coordinateColumnFold = [i, col_id_main];
            
            // 配列から該当する座標を削除
            const indexRowFold = AssignmentsForRowFold.findIndex(coord => 
                coord[0] === coordinateRowFold[0] && coord[1] === coordinateRowFold[1]);
            if (indexRowFold !== -1) {
                AssignmentsForRowFold.splice(indexRowFold, 1);
            }
            
            const indexColumnFold = AssignmentsForColumnFold.findIndex(coord => 
                coord[0] === coordinateColumnFold[0] && coord[1] === coordinateColumnFold[1]);
            if (indexColumnFold !== -1) {
                AssignmentsForColumnFold.splice(indexColumnFold, 1);
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
            
            // 座標形式で割当結果を追加
            const coordinateRowFold = [row_id_main, j];
            const coordinateColumnFold = [i, col_id_main];
            
            // 配列に座標を追加
            AssignmentsForRowFold.push(coordinateRowFold);
            AssignmentsForColumnFold.push(coordinateColumnFold);
            
            originalColors.set(cell_square, cell_square.style.backgroundColor);
            originalColors.set(cell_row_fold, cell_row_fold.style.backgroundColor);
            originalColors.set(cell_column_fold, cell_column_fold.style.backgroundColor);
            cell_square.style.backgroundColor = 'orange';
            cell_row_fold.style.backgroundColor = 'orange';
            cell_column_fold.style.backgroundColor = 'orange';
            sum += value;
        }
        
        // 割当結果を更新するメソッドを呼び出す
        updateAssignmentDisplays();
        
        document.getElementById('sum-display').innerText = '割当合計: ' + sum;
    }
    
    // 割当結果表示を更新する関数
    function updateAssignmentDisplays() {
        
        console.log("==================");
        console.log("割当結果");
        console.log(AssignmentsForRowFold);
        console.log(AssignmentsForColumnFold);
        console.log("==================");
        
        // row-foldテーブルの更新
        // 各行について割当結果を集計
        const rowAssignments = {};
        AssignmentsForRowFold.forEach(coordinate => {
            const [I, J] = coordinate;
            if (!rowAssignments[I]) {
                rowAssignments[I] = [];
            }
            // 割当列に対応する列名を取得
            const columnNameElement = document.querySelector(`th[id*="col-name-row-fold-${J}"]`);
            if (columnNameElement) {
                rowAssignments[I].push(columnNameElement.getAttribute('assignment_name'));
            }
        });

        // 行割当結果を更新 (row-fold テーブル)
        const rowFoldRowCount = document.querySelectorAll('th[id^="row-assignment-row-fold-"]').length;
        for (let i = 0; i < rowFoldRowCount; i++) {
            const assignmentCell = document.querySelector(`th[id="row-assignment-row-fold-${i}"]`);
            if (assignmentCell) {
                if (rowAssignments[i] && rowAssignments[i].length > 0) {
                    assignmentCell.innerText = rowAssignments[i].join(' ');
                } else {
                    assignmentCell.innerText = '';
                }
            }
        }
        
        // column-foldテーブルの更新
        // 各行について割当結果を集計
        const columnFoldRowAssignments = {};
        AssignmentsForColumnFold.forEach(coordinate => {
            const [I, J] = coordinate;
            if (!columnFoldRowAssignments[I]) {
                columnFoldRowAssignments[I] = [];
            }
            // 割当列に対応する列名を取得
            const columnNameElement = document.querySelector(`th[id*="col-name-column-fold-${J}"]`);
            if (columnNameElement) {
                columnFoldRowAssignments[I].push(columnNameElement.getAttribute('assignment_name'));
            }
        });
        
        // 行割当結果を更新 (column-fold テーブル)
        const columnFoldRowCount = document.querySelectorAll('th[id^="row-assignment-column-fold-"]').length;
        for (let i = 0; i < columnFoldRowCount; i++) {
            const assignmentCell = document.querySelector(`th[id="row-assignment-column-fold-${i}"]`);
            if (assignmentCell) {
                if (columnFoldRowAssignments[i] && columnFoldRowAssignments[i].length > 0) {
                    assignmentCell.innerText = columnFoldRowAssignments[i].join(' ');
                } else {
                    assignmentCell.innerText = '';
                }
            }
        }
        
        // 列に対しても同様の処理を行う
        // 各列について割当結果を集計
        const colAssignments = {};
        AssignmentsForRowFold.forEach(coordinate => {
            const [I, J] = coordinate;
            if (!colAssignments[J]) {
                colAssignments[J] = [];
            }
            // 割当行に対応する行名を取得
            const rowNameElement = document.querySelector(`th[id*="row-name-row-fold-${I}"]`);
            if (rowNameElement) {
                colAssignments[J].push(rowNameElement.getAttribute('assignment_name'));
            }
        });
        
        // 列割当結果を更新 (row-fold テーブル)
        const rowFoldColCount = document.querySelectorAll('th[id^="col-assignment-row-fold-"]').length;
        for (let j = 0; j < rowFoldColCount; j++) {
            const assignmentCell = document.querySelector(`th[id="col-assignment-row-fold-${j}"]`);
            if (assignmentCell) {
                if (colAssignments[j] && colAssignments[j].length > 0) {
                    assignmentCell.innerText = colAssignments[j].join(' ');
                } else {
                    assignmentCell.innerText = '';
                }
            }
        }
        
        // column-foldテーブルでも同様に列の処理を行う
        const colAssignmentsColumnFold = {};
        AssignmentsForColumnFold.forEach(coordinate => {
            const [I, J] = coordinate;
            if (!colAssignmentsColumnFold[J]) {
                colAssignmentsColumnFold[J] = [];
            }
            const rowNameElement = document.querySelector(`th[id*="row-name-column-fold-${I}"]`);
            if (rowNameElement) {
                colAssignmentsColumnFold[J].push(rowNameElement.getAttribute('assignment_name'));
            }
        });
        
        // 列割当結果を更新 (column-fold テーブル)
        const columnFoldColCount = document.querySelectorAll('th[id^="col-assignment-column-fold-"]').length;
        for (let j = 0; j < columnFoldColCount; j++) {
            const assignmentCell = document.querySelector(`th[id="col-assignment-column-fold-${j}"]`);
            if (assignmentCell) {
                if (colAssignmentsColumnFold[j] && colAssignmentsColumnFold[j].length > 0) {
                    assignmentCell.innerText = colAssignmentsColumnFold[j].join(' ');
                } else {
                    assignmentCell.innerText = '';
                }
            }
        }
    }
    </script>
    """