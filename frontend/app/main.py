import streamlit as st

# Load configuration from a settings file
image_path = "./PBLフライヤー1Q.jpg"

# Display side menu
with st.sidebar:
    st.page_link("main.py", label="ホーム", icon="🏠")
    st.page_link("pages/upload_files.py", label=
                 "ファイルアップロード・AI学習帳作成", icon="1⃣")
    st.page_link("pages/upload_files.py", label=
                 "ノート", icon="2⃣")
    st.page_link("pages/upload_files.py", label=
                 "AIサポートテスト", icon="3⃣")
    st.page_link("pages/upload_files.py", label=
                 "ファイル一覧""（学習帳・AIサポートテスト作成）", icon="4⃣")

# Display the image
st.image(image_path)
