import numpy as np
import random
import ExtendedMunkres
from munkres import make_cost_matrix

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

    #利益行列をコスト行列に変換
    if matrix_type == 1:
        cost_matrix = make_cost_matrix(original_matrix)
        #print("cost_matrix")
        #print(cost_matrix)
    else:
        cost_matrix = original_matrix

    result = m.compute(cost_matrix)
    assignment_matrix = m.get_internal_C()

    # 優先順位に基づいて割り当てを行う
    if priority_flag == 1:
        # 列優先
        # ... 列ごとの優先順位に基づく割り当て処理を実装 ...
        pass
    else:
        # 行優先
        # ... 行ごとの優先順位に基づく割り当て処理を実装 ...
        pass

    # 確定しない部分は乱数で決める
    # ... 乱数による割り当て処理を実装 ...

    # 割当利益orコストの総和を計算
    total_assignment = 0
    for (i, j) in result:
        total_assignment += original_matrix[i][j]

    return assignment_matrix, total_assignment

        # r = []
        # c = []
        # for v in zero_coordinate:
        #     if v[0] not in r and v[1] not in c:
        #         self.optimal.append(v)
        #         r.append(v[0])
        #         c.append(v[1])
        # return self.optimal