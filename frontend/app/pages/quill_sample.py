import re

import streamlit as st
from streamlit_quill import st_quill

# 最大ページ数
MAX_PAGES = 100

# セッション状態の初期化
if "page_content" not in st.session_state:
    st.session_state.page_content = {"page1": ""}


# HTMLをマークダウンに変換
def html_to_markdown(html_text: str) -> str:
    # HTMLタグを除去しつつ、段落の区切りを保持
    text = re.sub(r"<p>(.*?)</p>", r"\1\n\n", html_text, flags=re.DOTALL)
    # 空の段落（<p><br></p>）を単一の改行に変換
    text = re.sub(r"<p><br></p>", "\n", text)
    # 残りのHTMLタグを除去
    text = re.sub(r"<.*?>", "", text)
    # 見出しを適切なマークダウンに変換
    text = re.sub(
        r"^#+\s*(.+)$",
        lambda m: "#" * (m.group(0).count("#")) + " " + m.group(1),
        text,
        flags=re.MULTILINE,
    )
    # リストアイテムを適切なマークダウンに変換
    text = re.sub(r"^\*+\s*(.+)$", r"* \1", text, flags=re.MULTILINE)
    # 番号付きリストを適切なマークダウンに変換
    text = re.sub(r"^(\d+)\.\s*(.+)$", r"\1. \2", text, flags=re.MULTILINE)
    # 強調表現（太字）を保持
    text = re.sub(r"\*\*(.+?)\*\*", r"**\1**", text)
    # 連続する空行を1つにまとめる
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 先頭と末尾の空白行を削除
    text = text.strip()
    return text


# ページの内容を表示
def display_note_content() -> None:
    # ボタンの配置
    col1, col2, col3, _ = st.columns([1, 1, 1, 1])
    with col1:
        edit_button = st.button("テキスト編集", use_container_width=True)
    with col2:
        preview_button = st.button("プレビュー表示", use_container_width=True)

    with col3:
        markdown_button = st.button("マークダウン表示", use_container_width=True)

    # ボタンのアクション
    if preview_button:
        st.session_state.show_preview = "html"
    if edit_button:
        st.session_state.show_preview = "edit"
    if markdown_button:
        st.session_state.show_preview = "markdown"

    # プレビューモードの切り替え
    if st.session_state.show_preview == "html":
        st.html(st.session_state.page_content[st.session_state.current_page])
    elif st.session_state.show_preview == "markdown":
        st.markdown(
            html_to_markdown(
                st.session_state.page_content[st.session_state.current_page]
            )
        )
    else:
        # Quill editorを利用
        content = st_quill(
            value=st.session_state.page_content[
                st.session_state.current_page
            ],  # 現在のページの内容を表示
            html=True,
            placeholder="テキストをここに入力して下さい",
            key=f"quill_{st.session_state.current_page}",  # ページごとにキーを使用
        )
        st.session_state.page_content[st.session_state.current_page] = (
            content  # 現在のページの内容を更新
        )

    # 保存ボタン
    _, _, _, save_col = st.columns([1, 1, 1, 1])
    with save_col:
        if st.button("保存", use_container_width=True):
            # 保存処理
            st.success("保存しました！")


# 新しいページを作成
def create_new_page() -> None:
    if len(st.session_state.page_content) >= MAX_PAGES:
        st.error(
            f"ページ数が上限（{MAX_PAGES}ページ）に達しました。これ以上ページを作成できません。"
        )
        return

    # 新しいページ名を生成
    new_page_num = len(st.session_state.page_content) + 1
    new_page_name = f"page{new_page_num}"

    # 新しいページを追加
    st.session_state.page_content[new_page_name] = ""
    st.session_state.current_page = new_page_name
    st.success(f"新しいページ '{new_page_name}' を作成しました。")


def main() -> None:
    st.set_page_config(layout="wide")

    # セッション状態の初期化
    if "show_preview" not in st.session_state:
        st.session_state.show_preview = "edit"
    if is_content_empty(st.session_state.page_content["page1"]):
        # study_ai_note セッションがある場合、最初のページにその内容を設定
        if "study_ai_note" in st.session_state:
            st.session_state.page_content = {"page1": st.session_state.study_ai_note}
        else:
            st.session_state.page_content = {"page1": ""}  # 初期ページを1つだけ作成
    if "current_page" not in st.session_state:
        st.session_state.current_page = "page1"

    # 説明を表示
    st.text("Quill editorのサンプル")

    # サイドバー
    with st.sidebar:
        # ページ選択
        page = st.selectbox(
            "ページを選択",
            list(st.session_state.page_content.keys()),
            index=list(st.session_state.page_content.keys()).index(
                st.session_state.current_page
            ),
        )

        # 新しいページ作成ボタン
        if st.button("新しいページを作成", use_container_width=True):
            create_new_page()

        # 現在のページ数と最大ページ数を表示
        st.write(
            f"作成したページ数: {len(st.session_state.page_content)} / {MAX_PAGES}"
        )

        # ページが変更された場合、現在のページを更新
        if page != st.session_state.current_page:
            st.session_state.current_page = page

    # 選択されたページに応じてコンテンツを表示
    st.header(f"AIサポート学習帳 - {st.session_state.current_page}")
    st.write(f"AIサポート学習帳の{st.session_state.current_page}です。")

    # 全てのページで同じノート機能を表示
    display_note_content()


# ページの内容が空かどうかを判定
def is_content_empty(content: str) -> bool:
    # HTMLタグを除去し、空白文字をトリム
    stripped_content = re.sub(r"<[^>]+>", "", content).strip()
    return not bool(stripped_content)


if __name__ == "__main__":
    main()
