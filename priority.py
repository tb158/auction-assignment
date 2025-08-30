import numpy as np
import random


def decisionPriority(cost_matrix, col_priority, row_priority, priority_flag):
    """
    優先順位の高い順からcost_matrixでより低い値を割り当てる

    Parameters:
    -----------
    cost_matrix : numpy.ndarray
        コスト行列
    col_priority : list
        列ごとの優先順位
    row_priority : list
        行ごとの優先順位
    priority_flag : int
        優先順位のフラグ（0: 行優先, 1: 列優先）


    Returns:
    --------
    priority : list
        割り当て優先順位の高い順位に座標が格納されたリスト [(row, col), ...]
    """
    priority = []

    

    # 優先順位に基づいて割り当てを行う
    if priority_flag == 1:
        # 列優先

        # アルゴリズム
        # !auction_matrixで100-100vs100-100の2択に分かれることはあれど、100-100vs100-98の2択に分かれることはない
        # 列優先順位の高い列順に、cost_matrixの値が小さいものから割り当てる
        # cost_matrixの値が同じ場合は乱数で決める(上記事実からこれで問題ないことがわかる)
        # 列優先順位が同じ列の集合では、見方が90度変わって、列ごとではなく行優先順位の高い行順にcost_matrixの値が小さいものから割り当てる
        # 行優先順位も同じならどの行から割り当てるか乱数で決める
        # 割り当てられるものがなくなったら直前の割当を取り消して変更する
        # 優先順位が同じ他の列の割当を妨害してしまった場合も取り消す(ロジック考え中)
        
        # 上記じゃロジック不十分(列優先順位が同じ列が複数ある時に、割り当ての順番が不適当なせいで同じ優先順位内の割り当ての合計値が低くなったり
        #                    割り当ての合計値が最大値になる割り当て方が複数ある時に、特定の割当を選ばないと、より優先順位の低いもの同士の
        #                    割当で優先順位の高い列が損してしまうケースが考えられる)
        
        #

        sorted_col_indices = sorted(range(len(col_priority)), key=lambda x: col_priority[x])
        for j in sorted_col_indices:
            # 行優先順位が同じ場合はランダムに並べ替える
            sorted_row_indices = sorted(range(len(row_priority)), key=lambda x: (row_priority[x], random.random()))
            for i in sorted_row_indices:
                priority.append((i, j))
    else:
        # 行優先
        # 完成したら列優先と同様の処理を格納
        
        pass

    # 確定しない部分は乱数で決める
    # ... 乱数による割り当て処理を実装 ...

    return assignments

        # r = []
        # c = []
        # for v in zero_coordinate:
        #     if v[0] not in r and v[1] not in c:
        #         self.optimal.append(v)
        #         r.append(v[0])
        #         c.append(v[1])
        # return self.optimal