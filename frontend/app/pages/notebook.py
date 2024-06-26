import re

import streamlit as st


def preprocess_markdown(text: str) -> str:
    lines = text.split("\n")
    lines = [line.rstrip() + "  " for line in lines]
    text = "\n".join(lines)

    patterns = [
        (r"^(#+)([^#\s])", r"\1 \2"),
        (r"^([-*+])([^\s])", r"\1 \2"),
        (r"^(\d+\.)([^\s])", r"\1 \2"),
        (r"^(>)([^\s])", r"\1 \2"),
        (r"^(\s*[-*+])([^\s])", r"\1 \2"),
        (r"^(\s*\d+\.)([^\s])", r"\1 \2"),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)

    return text


def display_note_content() -> None:
    # タイトル入力
    note_title: str = st.text_input("ノートのタイトル", key="note_title")

    st.subheader("ノート")

    # ボタンの配置
    col1, col2, _ = st.columns([1, 1, 2])
    with col1:
        edit_button = st.button("テキスト編集", use_container_width=True)
    with col2:
        preview_button = st.button("プレビュー表示", use_container_width=True)

    # ボタンのアクション
    if preview_button:
        st.session_state.show_preview = True
    if edit_button:
        st.session_state.show_preview = False

    # プレビューモードの切り替え
    if not st.session_state.show_preview:
        markdown_text: str = st.text_area(
            "テキストをここに入力してください",
            value=st.session_state.markdown_text,
            height=500,
            key="markdown_input",
        )
        st.session_state.markdown_text = markdown_text
    else:
        processed_text: str = preprocess_markdown(st.session_state.markdown_text)
        st.markdown(processed_text)

    # 保存ボタン
    _, _, _, save_col = st.columns([1, 1, 1, 1])
    with save_col:
        if st.button("保存", use_container_width=True):
            # 保存処理
            st.success("保存しました！")


def main() -> None:
    st.set_page_config(layout="wide")

    # セッション状態の初期化
    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False
    if "markdown_text" not in st.session_state:
        st.session_state.markdown_text = ""

    # サイドバー
    with st.sidebar:
        st.page_link("main.py", label="ホーム", icon="🏠")
        st.page_link("pages/upload_image.py", label="ファイルアップロード", icon="1️⃣")
        st.page_link("pages/input_text.py", label="テキスト入力", icon="2️⃣")
        st.page_link("pages/output_note.py", label="AIサポート学習帳", icon="3️⃣")
        st.page_link("pages/output_test.py", label="AIサポートテスト", icon="4️⃣")
        st.page_link("pages/flyer.py", label="PBL フライヤー")

        st.write("---")  # 区切り線

        # ページ選択
        page = st.selectbox("ページを選択", [f"page{i}" for i in range(1, 12)], index=0)

    # 選択されたページに応じてコンテンツを表示
    st.title(f"AIサポート学習帳 - {page}")
    st.write(f"AIサポート学習帳の{page}です。")

    # 全てのページで同じノート機能を表示
    display_note_content()


if __name__ == "__main__":
    main()
