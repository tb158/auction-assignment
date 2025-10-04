import string
import streamlit as st
import numpy as np
import re
import pandas as pd
import assignment
import streamlit.components.v1 as components
from app_js import get_js
from app_style import get_html_style

# ページの設定
st.set_page_config(layout="wide")

class MatrixDimensionError(Exception):
    """行と列の複製係数の和が一致しない場合に発生する例外"""
    pass

class ExpandableMatrixAndBackgrounds:
    """
    expand可能なマトリックスと背景情報を管理するクラス
    """

    def show_all_members(self):
        """
        このインスタンスの全てのメンバー変数の値を見やすく表示するテスト用メソッド
        """
        print("==== ExpandableMatrixAndBackgrounds メンバー変数一覧 ====")
        print(f"row_names: {self.row_names}")
        print(f"column_names: {self.column_names}")
        print(f"row_priorities: {self.row_priorities}")
        print(f"column_priorities: {self.column_priorities}")
        print(f"display_matrix: {self.display_matrix}")
        print(f"row_ids: {self.row_ids}")
        print(f"col_ids: {self.col_ids}")
        # folded_row_names, folded_column_names などがあれば追加
        if hasattr(self, "folded_row_names"):
            print(f"folded_row_names: {self.folded_row_names}")
        if hasattr(self, "folded_column_names"):
            print(f"folded_column_names: {self.folded_column_names}")
        print("===============================================")
    """
    expand可能なマトリックスと背景情報を管理するクラス
    """
    def __init__(self, row_names, column_names, row_priorities, column_priorities, display_matrix, row_ids = None, col_ids = None):
        self.row_names = row_names
        self.column_names = column_names
        self.row_priorities = row_priorities
        self.column_priorities = column_priorities
        self.display_matrix = display_matrix
        
        if row_ids is None:
            self.row_ids = [str(i) for i in range(len(display_matrix))]
        else:
            self.row_ids = row_ids
        if col_ids is None:
            self.col_ids = [str(i) for i in range(len(display_matrix[0]))]
        else:
            self.col_ids = col_ids

    def row_expanded(self, row_replication_factors):
        """
        行複製係数に従って行を複製した新しいインスタンスを生成するインスタンスメソッド

        Parameters
        ----------
        row_replication_factors : list of int
            行複製係数

        Returns
        -------
        ExpandableMatrixAndBackgrounds
            行複製後の新しいインスタンス
        """
        # selfのメンバー変数に対して複製を行う
        expanded_row_names, expanded_row_priorities, expanded_row_ids, self.folded_row_names = \
            self.expand_names_and_priorities_and_ids(
                self.row_names,
                self.row_priorities,
                row_replication_factors
            )

        # 列情報はそのまま
        return ExpandableMatrixAndBackgrounds(
            expanded_row_names,
            self.column_names,
            expanded_row_priorities,
            self.column_priorities,
            self.row_expand_matrix(self.display_matrix, row_replication_factors),
            expanded_row_ids,
            self.col_ids
        )

    def column_expanded(self, column_replication_factors):
        """
        列複製係数に従って列を複製した新しいインスタンスを生成するインスタンスメソッド

        Parameters
        ----------
        column_replication_factors : list of int
            列複製係数

        Returns
        -------
        ExpandableMatrixAndBackgrounds
            列複製後の新しいインスタンス
        """
        # selfのメンバー変数に対して複製を行う
        expanded_column_names, expanded_column_priorities, expanded_column_ids, self.folded_column_names = \
            self.expand_names_and_priorities_and_ids(
                self.column_names,
                self.column_priorities,
                column_replication_factors
            )
            
        # 行情報はそのまま
        return ExpandableMatrixAndBackgrounds(
            self.row_names,
            expanded_column_names,
            self.row_priorities,
            expanded_column_priorities,
            self.column_expand_matrix(self.display_matrix, column_replication_factors),
            self.row_ids,
            expanded_column_ids
        )
        
    def row_expand_matrix(self, numeric_matrix, row_replication_factors):
        """
        行複製係数に従って行列を展開する
        """
        return [row for row, factor in zip(numeric_matrix, row_replication_factors) for _ in range(factor)]

    def column_expand_matrix(self, numeric_matrix, col_duplication_factors):
        """
        列複製係数に従って行列を展開する
        """
        return [
            [value for value, factor in zip(row, col_duplication_factors) for _ in range(factor)]
            for row in numeric_matrix
        ]

    def create_square_matrix(self, numeric_matrix, row_replication_factors, column_replication_factors):
        """
        行列を複製係数に従って展開する
        """
        # 行複製係数の和と列複製係数の和が一致するかを検証
        if sum(row_replication_factors) != sum(column_replication_factors):
            raise MatrixDimensionError()

        # 行を複製
        row_expanded_matrix = self.row_expand_matrix(numeric_matrix, row_replication_factors)

        # 行・列ともに複製
        square_matrix = self.column_expand_matrix(row_expanded_matrix, column_replication_factors)

        return square_matrix
    
    def expand_names_and_priorities_and_ids(self, names, priorities, replication_factors):
        """
        名前と優先順位を複製係数に従って展開する
        """
        # 行または列の複製
        expanded_names = []
        expanded_priorities = []
        folded_names = []
        expanded_ids = []
        
        for i, (priority, factor) in enumerate(zip(priorities, replication_factors)):
            if i < len(names):
                name = names[i]
            else:
                name = ""
            if factor == 1:
                expanded_names.append(name)
                folded_names.append(name)
            else:
                expanded_names.extend([f"{name}{j+1}" for j in range(factor)])
                folded_names.append(name + " × " + str(factor))
            expanded_priorities.extend([priority] * factor)
            expanded_ids.extend([str(i) + "-" + str(j) for j in range(factor)])
        return expanded_names, expanded_priorities, expanded_ids, folded_names

def split_text_to_array(input_text):
    """
    入力テキストをタブ、スペース、改行で分割し、配列に変換する。
    """
    return re.split(r'[\t|\s|\r\n|\r|\n]', input_text)

def parse_input_matrix(input_text):
    # 入力されたテキストを行列に変換
    lines = re.split(r'\r\n|\r|\n', input_text)
    matrix = [re.split(r'\s', line) for line in lines]
    return matrix

def calculate_priority_ranking(values):
    # 値の合計を計算
    sums = np.sum(values, axis=0)
    # ランキングを計算
    ranks = pd.Series(sums).rank(method='min', ascending=False).astype(int)
    return ranks.tolist()


def create_display_html_table_content(
    display_matrix_info : ExpandableMatrixAndBackgrounds,
    table_type : str,
    assignment_matrix=None
):
    m = display_matrix_info
    
    display_rows = len(m.display_matrix) + 2
    display_cols = len(m.display_matrix[0]) + 2
    # HTMLテーブルを作成
    html_table = f"""
    <div class='center-table'>
        <div class='table-container'>
            <table class='no-border-table'>
    """
    for i in range(display_rows):
        html_table += "<tr>"
        for j in range(display_cols):
            I = i-1
            J = j-1
            
            if i == 0 and j == 0:
                # 左上のセルに特定のクラスを追加
                html_table += f"<td class='top-left-cell'></td>"
            elif i == 0 and j == display_cols - 1:
                # 右上のセルに特定のクラスを追加
                html_table += f"<td class='top-right-cell'></td>"
            elif i == display_rows - 1 and j == display_cols - 1:
                # 右下のセルに特定のクラスを追加
                html_table += f"<td class='bottom-right-cell'></td>"
            elif i == display_rows - 1 and j == 0:
                # 左下のセルに特定のクラスを追加
                html_table += f"<td class='bottom-left-cell'></td>"
            else:
                if i == 0:
                    # 列名を薄い青色にし、列名は縦書きで上から下に表示する
                    cell_style = "writing-mode: vertical-lr;"
                    html_table += f"<th><span style='{cell_style}'>{m.column_names[J]}</span></th>"
                elif j == 0:
                    # 行名を薄い青色にする
                    cell_style = "background-color: #d3f9f9;"
                    html_table += f"<th><span style='{cell_style}'>{m.row_names[I]}</span></th>"
                elif i == display_rows - 1:
                    # 優先順位を薄緑色にする
                    cell_style = "background-color: #ccffcc;"
                    html_table += f"<td style='{cell_style}'>{m.column_priorities[J]}</td>"
                elif j == display_cols - 1:
                    # 優先順位を薄緑色にする
                    cell_style = "background-color: #ccffcc;"
                    html_table += f"<td style='{cell_style}'>{m.row_priorities[I]}</td>"
                else:
                    # display_matrixの値をdata属性に設定
                    cell_style = ""
                    if table_type == "square":
                        if assignment_matrix[I][J] == 0:
                            # 割り当てるべきセルは黄色にする
                            cell_style = "background-color: #ffffe0;"
                        # 最適自動割当のため、idは単純な座標から参照できるようにする
                        html_table += f"<td id = 'cell-{table_type}-{I}-{J}' row_id='{m.row_ids[I]}' col_id='{m.col_ids[J]}' style='{cell_style}' data-value='{m.display_matrix[I][J]}' onclick='toggleCellColor({I}, {J})'>{m.display_matrix[I][J]}</td>"
                    else:
                        html_table += f"<td id = 'cell-{table_type}-{I}-{J}' row_id='{m.row_ids[I]}' col_id='{m.col_ids[J]}' style='{cell_style}' data-value='{m.display_matrix[I][J]}'>{m.display_matrix[I][J]}</td>"
        html_table += "</tr>"
            
    html_table += f"""
            </table>
            <div class='vertical-label'>行優先順位</div>
        </div>
        <div style='text-align: center; font-weight: bold; width: 100%;'>列優先順位</div>
    </div>
    """
    
    return html_table
                    
def set_test_data():
    """
    テストデータをセッション状態に設定するメソッド
    """
    # テスト用の行列データ
    test_matrix = """	33	10	30	1		55		100	1				0
100		10		1		50	44		1		100	80	0
100	33	10		1		55	100		1			90	0
	33	10		1	100		88	100	1	100		70	0
	1	10		1		90			1				100
		10	90	1		60	99		1				0"""
    
    # テスト用の列名データ
    test_column_names = "アライ	オリベ	モモ	コジカ	マルベリー	アウグスト	ツユ	ハニー	シュアン	シェンミィ	ヒゴ	スズ	ヤマト	グレイ"
    
    # テスト用の行名データ
    test_row_names = "狼\n狂\n守\n占\n霊\n村"
    
    # セッション状態に設定
    st.session_state.test_input_matrix = test_matrix
    st.session_state.test_column_names = test_column_names
    st.session_state.test_row_names = test_row_names


def main():
    st.title("割当計算機")
    
    # テスト用のボタンを追加
    if st.button("テストデータを入力", help="※テスト用"):
        set_test_data()
        st.rerun()

    # 列名の入力用テキストエリア
    # セッション状態からテストデータを取得（存在する場合）
    default_column_names = st.session_state.get('test_column_names', '')
    
    column_names_text = st.text_area(
        "タブorスペースor改行区切りで各列の列名を貼り付けてください(任意)", 
        value=default_column_names,
        height=68,
        placeholder="アライ オリベ モモ コジカ マルベリー"
    )    
    # 行名の入力用のテキストエリア
    # セッション状態からテストデータを取得（存在する場合）
    default_row_names = st.session_state.get('test_row_names', '')
    
    row_names_text = st.text_area(
        "タブorスペースor改行区切りで各行の行名を貼り付けてください(任意)", 
        value=default_row_names,
        height=68,
        placeholder="狼\r\n狂\r\n守\r\n占\r\n霊"
    )
   
    # テキストエリアでデータを入力
    # セッション状態からテストデータを取得（存在する場合）
    default_value = st.session_state.get('test_input_matrix', '')
    
    input_matrix = st.text_area("TVS形式の行列を貼り付けてください",
                              value=default_value,
                              placeholder="10 20 30 40 50\r\n10 20 30 40 50\r\n10 20 30 40 50\r\n10 20 30 40 50\r\n10 20 30 40 50"
                              )
    
        
    # エラーメッセージ
    error_message = ""

    if input_matrix:
        # 入力をパースして行列に変換
        matrix = parse_input_matrix(input_matrix)
        
        # 行列の行数と列数を取得
        rows = len(matrix)
        cols = max(len(row) for row in matrix)

        try:
            # 空文字列を0に変換して数値に変換
            numeric_matrix = np.array([[cell if cell != '' else 0 for cell in row] for row in matrix], dtype=int)

            # 列優先順位を計算
            column_priorities = calculate_priority_ranking(numeric_matrix)

            # 行優先順位を計算
            row_priorities = calculate_priority_ranking(numeric_matrix.T)

        except ValueError as e:
            # 数値に変換できない場合や他のエラーの場合はエラーメッセージを設定
            error_message = "長方形の整数のみの行列を入力してください (空は0に変換するので許容)"
            column_priorities = [''] * cols
            row_priorities = [''] * rows

        # 行複製係数と列複製係数を追加
        # テストデータが入力されている場合は特定の値を設定
        if st.session_state.get('test_input_matrix'):
            row_replication_factors = ['4', '1', '1', '1', '1', '7']
            column_replication_factors = ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '2']
        else:
            row_replication_factors = ['1'] * rows
            column_replication_factors = ['1'] * cols

        # 新しい行列を作成
        new_matrix = [[''] * (cols + 2) for _ in range(rows + 2)]

        # 元の行列を中央に配置
        for i in range(rows):
            for j in range(len(matrix[i])):
                #new_matrix[i + 1][j + 1] = numeric_matrix[i][j]
                new_matrix[i + 1][j + 1] = matrix[i][j]

        # 行複製係数を左に追加
        for i in range(rows):
            new_matrix[i + 1][0] = row_replication_factors[i]

        # 列複製係数を上に追加
        for j in range(cols):
            new_matrix[0][j + 1] = column_replication_factors[j]

        # 行優先順位を右に追加
        for i in range(rows):
            new_matrix[i + 1][cols + 1] = str(row_priorities[i])

        # 列優先順位を下に追加
        for j in range(cols):
            new_matrix[rows + 1][j + 1] = str(column_priorities[j])

        # 1列目と1行目のラベルを「複」に設定
        new_matrix[0][0] = '複↓→'

        # 最終列と最終行のラベルを「優」に設定
        new_matrix[rows + 1][cols + 1] = '←↑優'

        df = pd.DataFrame(new_matrix)
        
        row_height = 20
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            hide_index=True,
            use_container_width=False,
            height=row_height * (rows + 2) + 57,
            width=None,
            row_height=20
        )
        # 行列の種類を選択（0: コスト行列, 1: 利益行列）
        matrix_type = st.radio(
            label="",
            options=[0, 1],
            format_func=lambda x: "利益行列" if x == 1 else "コスト行列",
            index=1,
            horizontal=True
        )

        # # 優先順位の種類を選択（0: 行優先, 1: 列優先）
        # priority_flg = st.radio(
        #     "優先順位が行も列も等しい最適割当が存在する場合にどちらを優先するか",
        #     options=[0, 1],
        #     format_func=lambda x: "行優先" if x == 0 else "列優先",
        #     index=1,
        #     horizontal=True
        # )
        priority_flg = 1

        if st.button("割当", use_container_width=True):

            st.markdown("<div style='text-align: center; font-size: 16px; margin: 10px 0;'>黄色のマスを割り当てていけば最適割当となります。</div>", unsafe_allow_html=True)

            # new_matrixをdfから設定
            new_matrix = edited_df.values.tolist()
            rows = len(new_matrix) - 2
            cols = max(len(row) for row in new_matrix) - 2

            try:
                # 行列の取得
                numeric_matrix = [
                    [int(new_matrix[i + 1][j + 1]) if new_matrix[i + 1][j + 1] != '' else 0 for j in range(cols)]
                    for i in range(rows)
                ]
                
                # 行名
                row_names = split_text_to_array(row_names_text)
                
                # 列名
                column_names = split_text_to_array(column_names_text)

                # 行複製係数
                row_replication_factors = [int(new_matrix[i + 1][0]) for i in range(rows)]

                # 列複製係数
                column_replication_factors = [int(new_matrix[0][j + 1]) for j in range(cols)]

                # 行優先順位
                row_priorities = [int(new_matrix[i + 1][cols + 1]) for i in range(rows)]

                # 列優先順位
                column_priorities = [int(new_matrix[rows + 1][j + 1]) for j in range(cols)]

                # ExpandableMatrixAndBackgroundsインスタンスを作成
                # 複製前
                original_matrix_info = ExpandableMatrixAndBackgrounds(row_names, column_names, row_priorities, column_priorities, numeric_matrix)
                # 行複製
                row_expanded_matrix_info = original_matrix_info.row_expanded(row_replication_factors)
                # 列複製
                column_expanded_matrix_info = original_matrix_info.column_expanded(column_replication_factors)
                
                # folded_namesを格納
                row_expanded_matrix_info.column_names = original_matrix_info.folded_column_names
                column_expanded_matrix_info.row_names = original_matrix_info.folded_row_names
                # 正方行列を作成しmatrix_infoに
                square_matrix = original_matrix_info.create_square_matrix(numeric_matrix, row_replication_factors, column_replication_factors)
                square_matrix_info = ExpandableMatrixAndBackgrounds(
                    row_expanded_matrix_info.row_names,
                    column_expanded_matrix_info.column_names,
                    row_expanded_matrix_info.row_priorities,
                    column_expanded_matrix_info.column_priorities,
                    square_matrix,
                    row_expanded_matrix_info.row_ids,
                    column_expanded_matrix_info.col_ids
                )
                
                # matrix_info確認用
                # row_expanded_matrix_info.show_all_members()
                # column_expanded_matrix_info.show_all_members()
                # original_matrix_info.show_all_members()
                # square_matrix_info.show_all_members()
                
                # 割当
                assignment_matrix, total_assignment = assignment.assign(square_matrix, square_matrix_info.row_priorities, square_matrix_info.column_priorities, priority_flg, matrix_type)

                    

                # ラジオボタンで表示モードを選択
                #display_mode = st.radio("表示モード:", ["正方表示", "行を折りたたむ", "列を折りたたむ"], index=0, label_visibility="hidden")
                # htmlのラジオボタンをテーブルの右に配置する予定
                # display_mode = "正方表示"
                # if display_mode == "正方表示":
                #     html_table += create_display_html_table_content(one_side, one_side, assignment_matrix, expanded_column_names, expanded_column_priorities, expanded_row_names, expanded_row_priorities, square_matrix)
                # elif display_mode == "行を折りたたむ":
                #     #以下実装中
                #     # fold_lists()
                #     # html_table += create_display_html_table_content(numeric_matrix.length, one_side, assignment_matrix, expanded_column_names, expanded_column_priorities, folded_row_names, expanded_row_priorities, square_matrix)
                # elif display_mode == "列を折りたたむ":
                #     html_table += create_display_html_table_content(one_side, numeric_matrix[0].length, assignment_matrix, folded_column_names, expanded_column_priorities, expanded_row_names, expanded_row_priorities, square_matrix)
                
                html_table_square = create_display_html_table_content(square_matrix_info, "square", assignment_matrix)
                html_table_row_fold = create_display_html_table_content(column_expanded_matrix_info, "row-fold")
                html_table_column_fold = create_display_html_table_content(row_expanded_matrix_info, "column-fold")
                

                # 右側にHTMLラジオを配置し、表示を切り替え
                html_table_with_radio = f"""
                <div style='display:flex; gap:16px; align-items:flex-start; justify-content:flex-start; flex-wrap: nowrap;'>
                  <div style='flex:1 1 auto; min-width:0; overflow:auto;'>
                    <div id='tbl_square'>{html_table_square}
                        <button onclick="resetAssignment()" style="display: block; margin: 10px auto;">割当リセット</button>
                    </div>
                    <div id='tbl_fold_rows' style='display:none;'>{html_table_row_fold}
                        <button onclick="resetAssignment()" style="display: block; margin: 10px auto;" disabled>割当リセット</button>
                    </div>
                    <div id='tbl_fold_cols' style='display:none;'>{html_table_column_fold}
                        <button onclick="resetAssignment()" style="display: block; margin: 10px auto;" disabled>割当リセット</button>
                    </div>
                  </div>
                  <div style='width:220px; flex:0 0 220px;'>
                    <label><input type='radio' name='display_mode_html' value='square' checked> 正方表示</label><br/>
                    <label><input type='radio' name='display_mode_html' value='fold_rows'> 行を折りたたむ(割当操作はできません)</label><br/>
                    <label><input type='radio' name='display_mode_html' value='fold_cols'> 列を折りたたむ(割当操作はできません)</label>
                  </div>
                </div>
                """
                
                html_table_tail = f"""<div style="display: flex; justify-content: center; text-align: center; margin-top: 20px; margin-right: 220px;">
                    <div id='sum-display' style="margin-right: 10px;">割当合計: 0</div>
                    <div>最適割当合計: {total_assignment}</div>
                </div>
                """

                # script
                html_js = get_js()

                # CSSスタイルを定義
                cell_size = 40  # セルのサイズを40pxに設定
                html_style = get_html_style(cell_size)

                # HTMLコンテンツを表示（ラジオで切替するが中身は同一）
                components.html(html_table_with_radio + html_table_tail + html_js + html_style, height=cell_size * len(square_matrix) + 500)

            except ValueError:
                error_message = "長方形の整数のみの行列を入力してください (空は0に変換するので許容)"
            except MatrixDimensionError:
                error_message = "行または列の複製後に正方形行列になるようにしてください (行複製係数の和と列複製係数の和を一致させてください)"

    # エラーメッセージを表示
    if error_message:
        st.markdown(f"<div style='color: red; text-align: center;'>{error_message}</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top: 600px;'>
        <h2>使い方</h2>
        <ul>
            <li>ハンガリアンアルゴリズムによる割当を計算します。</li>
            <li>下記の入力イメージを参考に、エクセルやスプレッドシートから行列をコピペしてください。</li>
            <li>複数係数を2以上に設定した場合は同じ行または列を直後に複製したものを計算します。</li>
            <li>現在は優先順位は計算には使用せず、メモ用に表示しています。</li>
            <li>優先順位の初期値は各行(または各列)の値の総和を順位化したものになっています。</li>
            <li>優先順位と複製係数もエクセルやスプレッドシートからコピペで上書きできます。</li>
            <li>行を誤って追加した場合は選択してバックスペースで削除できます。</li>
            <li>テストデータを入力ボタンを使用した場合は、実使用の前にブラウザ更新をかける必要があります</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 画像を表示
    st.image("image.png")

if __name__ == "__main__":
    main() 
