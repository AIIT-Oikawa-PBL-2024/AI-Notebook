import streamlit as st

# Load configuration from a settings file
image_path = "./PBLフライヤー1Q.jpg"
sidebar_links = [
    {"path": "main.py", "label": "ホーム", "icon": "🏠"},
    {"path": "pages/upload_files.py", "label": "ファイルアップロード", "icon": "1️⃣"},
]

# Display the image
st.image(image_path)

# Add sidebar links
with st.sidebar:
    for link in sidebar_links:
        st.page_link(link["path"], label=link["label"], icon=link["icon"])
