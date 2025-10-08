import numpy as np
import random
import ExtendedMunkres
from munkres import make_cost_matrix
from ortools.sat.python import cp_model

def assign(original_matrix, row_priorities, col_priorities, priority_flag, matrix_type):
    """
    優先順位の高い順から元の行列でより高い値を割り当てる

    Parameters:
    -----------
    original_matrix : numpy.ndarray
        元の行列
    col_priorities : list[int]
        列ごとの優先順位
    row_priorities : list[int]
        行ごとの優先順位
    priority_flag : int
        優先順位のフラグ（0: 行優先, 1: 列優先）
    matrix_type : int
        行列の種類(0ならコスト行列、1なら利益行列)

    Returns:
    --------
    assignments : list
        割り当てのリスト [(row, col), ...]
    """
    assignments = []
    m = ExtendedMunkres.ExtendedMunkres()

    # 利益行列をコスト行列に変換
    if matrix_type == 1:
        print("利益行列をコスト行列に変換")
        cost_matrix = make_cost_matrix(original_matrix)
    else:
        cost_matrix = original_matrix
        print(cost_matrix)

    result = m.compute(cost_matrix)
    original_assignment_matrix = m.get_internal_C()
    
    # 割当利益orコストの総和を計算
    total_assignment = 0
    for (i, j) in result:
        total_assignment += original_matrix[i][j]
    # 優先順位に基づいて割り当てを行う
    one_side = len(cost_matrix)

    # ランダムな行置換と列置換を生成
    row_permutation = list(range(one_side))
    col_permutation = list(range(one_side))
    random.shuffle(row_permutation)
    random.shuffle(col_permutation)
    
    print(f"=== シャッフル情報 ===")
    print(f"元の行順序: {list(range(one_side))}")
    print(f"新しい行順序: {row_permutation}")
    print(f"元の列順序: {list(range(one_side))}")
    print(f"新しい列順序: {col_permutation}")
    
    # 各変数に同じ対応でシャッフルを適用（置換を同時に適用）
    # cost_matrixの行と列を同時にシャッフル
    cost_matrix = [[cost_matrix[row_permutation[i]][col_permutation[j]] for j in range(one_side)] for i in range(one_side)]
    print(cost_matrix[0][0])
    
    # assignment_matrixの行と列を同時にシャッフル
    assignment_matrix = [[original_assignment_matrix[row_permutation[i]][col_permutation[j]] for j in range(one_side)] for i in range(one_side)]
    
    # row_prioritiesをシャッフル
    row_priorities = [row_priorities[row_permutation[i]] for i in range(one_side)]
    
    # col_prioritiesをシャッフル
    col_priorities = [col_priorities[col_permutation[j]] for j in range(one_side)]

    print(f"=== シャッフル後の情報 ===")
    print(f"シャッフル後のcost_matrix:")
    for i, row in enumerate(cost_matrix):
        print(f"  行{i}: {row}")
    print(f"シャッフル後のassignment_matrix:")
    for i, row in enumerate(assignment_matrix):
        print(f"  行{i}: {row}")
    print(f"シャッフル後のrow_priorities: {row_priorities}")
    print(f"シャッフル後のcol_priorities: {col_priorities}")
    print(f"=========================")
    
    # OR-Toolsによる最適化
    # assignment_matrix: 0が割当可能
    
    # OR-Tools CP-SATモデルの設定
    model = cp_model.CpModel()
    
    # 変数定義：各行に対してどの列に割り当てるかを決定
    row_vars = []
    for row in range(one_side):
        available_cols = [col for col in range(one_side) 
                         if assignment_matrix[row][col] == 0]
        var = model.NewIntVarFromDomain(
            cp_model.Domain.FromValues(available_cols), 
            f'row_{row}'
        )
        row_vars.append(var)
        # print(f'row_{row}: {available_cols}')
    
    # 制約：各行は異なる列に割り当てられる（全単射）
    model.AddAllDifferent(row_vars)
    
    # 3. 辞書式最適化の実装

    # priority_flgに基づいて最適化の順序を決定
    if priority_flag == 0:  # 行優先
        print("=== 行優先モード ===")
        # 第1優先: 行優先順位に基づく最小化
        current_solution = optimize_by_row_priorities(model, row_vars, row_priorities, assignment_matrix, cost_matrix, "第1優先")
        
        # 第2優先: 列優先順位に基づく最小化
        if current_solution:
            current_solution = optimize_by_column_priorities(model, row_vars, col_priorities, assignment_matrix, cost_matrix, "第2優先")
    else:  # 列優先
        print("=== 列優先モード ===")
        # 第1優先: 列優先順位に基づく最小化
        current_solution = optimize_by_column_priorities(model, row_vars, col_priorities, assignment_matrix, cost_matrix, "第1優先")
        
        # 第2優先: 行優先順位に基づく最小化
        if current_solution:
            current_solution = optimize_by_row_priorities(model, row_vars, row_priorities, assignment_matrix, cost_matrix, "第2優先")
    
    # 最終解
    if current_solution:
        assignments = current_solution
        print(f"=== 最終解の変換過程 ===")
        print(f"最終的な制約：{model.Proto().constraints}")
        print(f"最終解（シャッフル後）: {assignments}")
        
        # assignmentsを元の順序に戻す
        original_assignments = []
        # ロジック：置換後のn番目の値は元の行列のσ(n)番目の値が入っている→その値はどこからきたか→元の行列のσ(n)番目の値が来ている
        # よって単にσ(n)に戻せばいいのであって、逆置換は必要ない
        for i, (row, col) in enumerate(assignments):
            # シャッフルされた座標から元の座標に変換
            original_row = row_permutation[row]
            original_col = col_permutation[col]
            original_assignments.append((original_row, original_col))
            print(f"  割当{i}: ({row}, {col}) <- ({original_row}, {original_col})")
        
        assignments = original_assignments
        print(f"最終解（元の順序）: {assignments}")
        print(f"===================")
 
    return original_assignment_matrix, total_assignment, assignments

def make_sorted_priority_groups(priorities):
    """
    優先順位リストからソート済みの優先順位グループを作成する関数
    Parameters
    ----------
    priorities : list[int]
        行または列の優先順位リスト
    Returns
    -------
    sorted_priority_groups : list
        (優先順位, インデックスリスト)のタプルのリスト（優先順位でソート済み）
    """
    priority_groups = {}
    for idx, priority in enumerate(priorities):
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(idx)
    
    # 優先順位でソートしてタプルのリストとして返す
    sorted_priorities = sorted(priority_groups.keys())
    sorted_priority_groups = [(priority, priority_groups[priority]) for priority in sorted_priorities]
    return sorted_priority_groups

def create_cost_terms_in_cols(model, row_vars, current_cols, assignment_matrix, cost_matrix, prefix):
    """
    指定された列グループに対してコスト項を作成する関数
    Parameters
    ----------
    model : cp_model.CpModel
        OR-ToolsのCP-SATモデル
    row_vars : list
        行変数のリスト
    current_cols : list
        対象となる列のインデックスリスト
    assignment_matrix : numpy.ndarray
        割当可能行列（0が割当可能）
    cost_matrix : numpy.ndarray
        コスト行列
    prefix : str
        変数名のプレフィックス
    Returns
    -------
    terms : list
        コスト項のリスト
    """
    terms = []
    for row, var in enumerate(row_vars):
        for col in current_cols:
            if assignment_matrix[row][col] == 0:  # 割り当て可能な場合のみ
                is_assigned = model.NewBoolVar(f'{prefix}_row_{row}_col_{col}')
                model.Add(var == col).OnlyEnforceIf(is_assigned)
                model.Add(var != col).OnlyEnforceIf(is_assigned.Not())
                terms.append(cost_matrix[row][col] * is_assigned)
    return terms
def create_cost_terms_in_rows(model, row_vars, current_rows, assignment_matrix, cost_matrix, prefix):
    """
    指定された行グループに対してコスト項を作成する関数
    Parameters
    ----------
    model : cp_model.CpModel
        OR-ToolsのCP-SATモデル
    row_vars : list
        行変数のリスト
    current_rows : list
        対象となる行のインデックスリスト
    assignment_matrix : numpy.ndarray
        割当可能行列（0が割当可能）
    cost_matrix : numpy.ndarray
        コスト行列
    prefix : str
        変数名のプレフィックス
    Returns
    -------
    terms : list
        コスト項のリスト
    """
    terms = []
    for row in current_rows:
        for col in range(len(assignment_matrix[0])):
            if assignment_matrix[row][col] == 0:  # 割り当て可能な場合のみ
                is_assigned = model.NewBoolVar(f'{prefix}_row_{row}_col_{col}')
                model.Add(row_vars[row] == col).OnlyEnforceIf(is_assigned)
                model.Add(row_vars[row] != col).OnlyEnforceIf(is_assigned.Not())
                terms.append(cost_matrix[row][col] * is_assigned)
    return terms
def optimize_by_row_priorities(model, row_vars, row_priorities, assignment_matrix, cost_matrix, prefix_name):
    """
    行優先順位に基づく辞書式最適化を実行する関数
    Parameters
    ----------
    model : cp_model.CpModel
        OR-ToolsのCP-SATモデル
    row_vars : list
        行変数のリスト
    row_priorities : list[int]
        行優先順位リスト
    assignment_matrix : list or numpy.ndarray
        割当可能行列（0が割当可能）
    cost_matrix : list or numpy.ndarray
        コスト行列
    prefix_name : str
        処理名のプレフィックス（デバッグ用）
    Returns
    -------
    current_solution : list or None
        最適解のリスト、解が見つからない場合はNone
    """
    print(f"=== {prefix_name}: 行優先順位に基づく最小化 ===")
    sorted_row_priority_groups = make_sorted_priority_groups(row_priorities)
    print(f"行優先順位グループ: {dict(sorted_row_priority_groups)}")
    print(f"評価順序: {[priority for priority, _ in sorted_row_priority_groups]}")
    
    current_solution = None
    
    for row_priority, current_rows in sorted_row_priority_groups:
        print(f"\n行優先順位 {row_priority} のグループ {current_rows} を評価中...")
        
        objective_terms = create_cost_terms_in_rows(model, row_vars, current_rows, assignment_matrix, cost_matrix, f'obj_{prefix_name}_priority_{row_priority}')
        
        if objective_terms:
            model.Minimize(sum(objective_terms))
            
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL:
                # 解を取得
                current_solution = []
                for row, var in enumerate(row_vars):
                    col = solver.Value(var)
                    current_solution.append((row, col))
                
                # このグループの最小値を計算
                group_value = 0
                for assigned_row, assigned_col in current_solution:
                    if assigned_row in current_rows:
                        group_value += cost_matrix[assigned_row][assigned_col]
                
                print(f"  最小値: {group_value}")
                
                # 次の優先度で制約を追加
                # 対象行のコスト合計を制約として追加
                cost_terms = create_cost_terms_in_rows(model, row_vars, current_rows, assignment_matrix, cost_matrix, f'constraint_{prefix_name}_priority_{row_priority}')
                
                if cost_terms:
                    model.Add(sum(cost_terms) == group_value)
            else:
                print("  解が見つかりませんでした")
                current_solution = None
        
        model.ClearObjective()
    
    return current_solution
def optimize_by_column_priorities(model, row_vars, col_priorities, assignment_matrix, cost_matrix, prefix_name):
    """
    列優先順位に基づく辞書式最適化を実行する関数
    Parameters
    ----------
    model : cp_model.CpModel
        OR-ToolsのCP-SATモデル
    row_vars : list
        行変数のリスト
    col_priorities : list[int]
        列優先順位リスト
    assignment_matrix : list or numpy.ndarray
        割当可能行列（0が割当可能）
    cost_matrix : list or numpy.ndarray
        コスト行列
    prefix_name : str
        処理名のプレフィックス（デバッグ用）
    Returns
    -------
    current_solution : list or None
        最適解のリスト、解が見つからない場合はNone
    """
    print(f"=== {prefix_name}: 列優先順位に基づく最小化 ===")
    sorted_col_priority_groups = make_sorted_priority_groups(col_priorities)
    print(f"列優先順位グループ: {dict(sorted_col_priority_groups)}")
    print(f"評価順序: {[priority for priority, _ in sorted_col_priority_groups]}")
    
    current_solution = None
    
    for col_priority, current_cols in sorted_col_priority_groups:
        print(f"\n列優先順位 {col_priority} のグループ {current_cols} を評価中...")
        
        objective_terms = create_cost_terms_in_cols(model, row_vars, current_cols, assignment_matrix, cost_matrix, f'obj_{prefix_name}_priority_{col_priority}')
        
        if objective_terms:
            model.Minimize(sum(objective_terms))
            
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL:
                # 解を取得
                current_solution = []
                for row, var in enumerate(row_vars):
                    col = solver.Value(var)
                    current_solution.append((row, col))
                
                # このグループの最小値を計算
                group_value = 0
                for row, (assigned_row, assigned_col) in enumerate(current_solution):
                    if assigned_col in current_cols:
                        group_value += cost_matrix[assigned_row][assigned_col]
                
                print(f"  最小値: {group_value}")
                
                # 次の優先度で制約を追加
                # 対象列のコスト合計を制約として追加
                cost_terms = create_cost_terms_in_cols(model, row_vars, current_cols, assignment_matrix, cost_matrix, f'constraint_{prefix_name}_priority_{col_priority}')
                
                if cost_terms:
                    model.Add(sum(cost_terms) == group_value)
            else:
                print("  解が見つかりませんでした")
                current_solution = None
        
        model.ClearObjective()
    
    return current_solution
# 以下テスト用


def test_lexicographic_optimization_full():
    """
    辞書式最適化の全段階をテストする関数
    """
    # 制約を緩和したテスト用の行列（全ての位置が割り当て可能）
    original_matrix = np.array([
        [5, 15, 25],
        [15, 5, 25],
        [25, 25, 5]
    ])
    
    row_priorities = [1, 1, 2]  # 行0と行1が同じ優先順位
    col_priorities = [1, 1, 2]  # 列0と列1が同じ優先順位
    priority_flag = 1
    matrix_type = 0
    
    print("\n=== 全段階辞書式最適化テスト ===")
    print("original_matrix:")
    print(original_matrix)
    print(f"row_priorities: {row_priorities}")
    print(f"col_priorities: {col_priorities}")
    print()
    
    # 制約を緩和するためにassignment_matrixを全て0にする
    # 実際のassign関数内でassignment_matrixが全て0になるように調整
    assignment_matrix_result, total_assignment, assignments = assign(
        original_matrix, row_priorities, col_priorities, priority_flag, matrix_type
    )
    
    print(f"total_assignment: {total_assignment}")
    print(f"assignments: {assignments}")
    return assignment_matrix_result, total_assignment, assignments




if __name__ == "__main__":
    # テスト実行
    test_lexicographic_optimization_full()
    
