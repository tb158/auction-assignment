import streamlit as st
import numpy as np
from solveLogic import Hungarian

def main():
    st.title("ハンガリアンアルゴリズムによる割当問題ソルバー")
    
    # サンプルの4×4コスト行列
    a = [5, 4, 7, 6]
    b = [6, 7, 3, 2]
    c = [8, 11, 2, 5]
    d = [9, 8, 6, 7]
    cost_matrix = np.array([a, b, c, d])
    
    st.write("## コスト行列")
    st.write(cost_matrix)
    
    # Hungarianクラスを使用して解く
    h = Hungarian()
    assignments = h.compute(cost_matrix)
    
    # 結果を表示
    st.write("## 最適な割り当て")
    for row, col in assignments:
        st.write(f"ワーカー {row} にタスク {col} を割り当て (コスト: {cost_matrix[row, col]})")
    
    # 総コストを計算
    total_cost = sum(cost_matrix[row, col] for row, col in assignments)
    st.write(f"## 最小総コスト: {total_cost}")
    
    # 結果行列を作成
    result_matrix = np.zeros_like(cost_matrix)
    for row, col in assignments:
        result_matrix[row, col] = cost_matrix[row, col]
    
    st.write("## ハンガリアンアルゴリズムを適用し終わった行列")
    st.write(result_matrix)

if __name__ == "__main__":
    main() 