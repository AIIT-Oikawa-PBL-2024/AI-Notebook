import streamlit as st


def main() -> None:
    st.set_page_config(layout="wide")

    # サイドバー
    with st.sidebar:
        st.page_link("main.py", label="ホーム", icon="🏠")
        st.page_link("pages/upload_image.py", label="ファイルアップロード", icon="1️⃣")
        st.page_link("pages/input_text.py", label="テキスト入力", icon="2️⃣")
        st.page_link("pages/output_note.py", label="AIサポート学習帳", icon="3️⃣")
        st.page_link("pages/output_test.py", label="AIサポートテスト", icon="4️⃣")
        st.page_link("pages/flyer.py", label="PBL フライヤー")

    # タイトル入力
    title = st.text_input("エディタのタイトル", "無題のノート")
    st.title(title)

    # 2列レイアウト
    col1, col2 = st.columns(2)

    # 左側：マークダウン入力
    with col1:
        st.subheader("自由入力")
        markdown_text = st.text_area("マークダウンで記入してください", height=500)
        st.markdown(markdown_text)

    # 右側：AI要約結果（編集可能）
    with col2:
        st.subheader("AI要約結果")
        ai_summary = st.text_area(
            "AI生成の要約（編集可能）",
            "ここにAI生成の要約が表示されます。編集も可能です。",
            height=500,
        )

    # 保存ボタン
    _, _, _, save_col = st.columns([1, 1, 1, 1])
    with save_col:
        if st.button("保存", use_container_width=True):
            # ここに保存のロジックを実装
            st.success("保存しました！")


if __name__ == "__main__":
    main()
