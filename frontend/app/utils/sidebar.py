import streamlit as st


def show_sidebar() -> None:
    with st.sidebar:
        st.page_link("main.py", label="ホーム", icon="🏠")
        st.page_link("pages/select_files.py", label="ファイル選択", icon="📁")
        st.page_link(
            "pages/study_ai_note.py", label="ノート・AIサポート学習帳", icon="🗒️"
        )
        # st.page_link("pages/upload_image.py", label="ファイルアップロード"")
        # st.page_link("pages/input_text.py", label="テキスト入力", icon="")
        # st.page_link("pages/output_note.py", label="AIサポート学習帳", icon="")
        # st.page_link("pages/output_test.py", label="AIサポートテスト", icon="")
