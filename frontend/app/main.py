import streamlit as st

# ./PBLフライヤー1Q.jpg　を表示する
st.image("./PBLフライヤー1Q.jpg")
with st.sidebar:
    st.page_link("main.py", label="ホーム", icon="🏠")
    st.page_link("pages/upload_files.py", label="ファイルアップロード", icon="1️⃣")
