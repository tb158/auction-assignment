def get_html_style(cell_size):
    return f"""
    <style>
    /* ダークモードでも読めるように、埋め込み側で白背景・黒文字を基調にする */
    html, body {{
        background: #ffffff !important;
        color: #000000 !important;
    }}
    .center-table {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
        background: #ffffff !important;
        color: #000000 !important;
    }}
    .table-container {{
        display: flex;
        align-items: center;
        background: #ffffff !important;
        color: #000000 !important;
    }}
    .vertical-label {{
        writing-mode: vertical-rl;
        text-orientation: upright;
        margin-left: 10px;
        font-weight: bold;
        color: #000000 !important;
    }}
    .horizontal-label {{
        text-align: center; 
        font-weight: bold; 
        color: #000000 !important;
    }}
    .no-border-table, .no-border-table tr {{
        border: none;
    }}
    table {{
        border-collapse: collapse;
        table-layout: auto;  /* fixedからautoに変更 */
        width: max-content;  /* 内容に合わせて自動調整 */
        background: #ffffff; /* デフォルト白（インライン指定があればそちら優先） */
        color: #000000;
    }}
     /* 割り当て結果セル専用のスタイル */
     th[id*="row-assignment"] {{
         height: {cell_size}px;
         overflow: visible;    /* 内容をすべて表示 */
         white-space: nowrap;  /* 改行を防ぐ */
         border: 1px solid #000;
         text-overflow: ellipsis;  /* 超過した部分を省略記号で表示 */
         text-align: left !important;  /* 左づめに設定 */
         padding-left: 4px;  /* 左側にパディングを追加 */
     }}
    /* 割り当て結果セル専用のスタイル */
    th[id*="col-assignment"] {{
        width: {cell_size}px;
        white-space: normal;  /* 改行を許可 */
        word-wrap: break-word; /* 長い単語を改行 */
        overflow: visible;    /* 内容をすべて表示 */
        border: 1px solid #000;
    }}
    /* 通常のヘッダーセル（列名・行名）のスタイル */
    th:not([id*="assignment"]) {{
        max-width: 160px;  /* 最大幅を80pxに設定 */
        overflow: hidden;  /* 超過した部分を隠す */
        white-space: nowrap;  /* 改行を防ぐ */
        text-overflow: clip;  /* 超過した部分を切り取る */
        border: 1px solid #000;
    }}
    td {{
        width: {cell_size}px;
        height: {cell_size}px;
        text-align: center !important;
        overflow: hidden;
        white-space: nowrap;
        border: 1px solid #000;
    }}
    .priority-text {{
        text-align: center;
        font-weight: bold;
    }}
    .row-priority {{
        writing-mode: horizontal-tb;
    }}
    .column-priority {{
        writing-mode: vertical-rl;
        text-orientation: upright;
        height: 100px;
    }}
    /* 四隅のセルのスタイルを変更 */
    .no-border-table .corner-cell {{
        background-color: transparent;  /* 背景色を無しにする */
        contenteditable: false !important;
        border-top: none;
        border-bottom: none;
        border-right: none;
        border-left: none;
    }}
    </style>
    """
