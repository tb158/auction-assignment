def get_html_style(cell_size):
    return f"""
    <style>
    .center-table {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
    }}
    .table-container {{
        display: flex;
        align-items: center;
    }}
    .vertical-label {{
        writing-mode: vertical-rl;
        text-orientation: upright;
        margin-left: 10px;
        font-weight: bold;
    }}
    .horizontal-label {{
        text-align: center; 
        font-weight: bold; 
    }}
    .no-border-table, .no-border-table tr {{
        border: none;
    }}
    table {{
        border-collapse: collapse;
        table-layout: fixed;
    }}
    th {{
        max-width: 160px;  /* 最大幅を80pxに設定 */
        overflow: hidden;  /* 超過した部分を隠す */
        white-space: nowrap;  /* 改行を防ぐ */
        text-overflow: clip;  /* 超過した部分を切り取る */
        border: 1px solid #000;
        background-color: #d3f9f9;
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
    /* 左上のセルのスタイルを変更 */
    .no-border-table .top-left-cell {{
        background-color: transparent;  /* 背景色を無しにする */
        contenteditable: false !important;
        border-top: none;
        border-left: none;
    }}
    /* 右上のセルのスタイルを変更 */
    .no-border-table .top-right-cell {{
        background-color: transparent;  /* 背景色を無しにする */
        contenteditable: false !important;
        border-top: none;
        border-right: none;
    }}
    /* 右下のセルのスタイルを変更 */
    .no-border-table .bottom-right-cell {{
        background-color: transparent;  /* 背景色を無しにする */
        contenteditable: false !important;
        border-right: none;
        border-bottom: none;
    }}
    /* 左下のセルのスタイルを変更 */
    .no-border-table .bottom-left-cell {{
        background-color: transparent;  /* 背景色を無しにする */
        contenteditable: false !important;
        border-left: none;
        border-bottom: none;
    }}
    </style>
    """
