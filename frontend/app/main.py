import json

import streamlit as st

# Load configuration from a settings file
with open("config.json", "r") as f:
    config = json.load(f)
sidebar_links = config["sidebar_links"]
sidebar_links = [
    {"path": "pages/upload_files.py", "label": "ファイルアップロード", "icon": "1️⃣"},
]

# Define the image path
image_path = "path/to/image.jpg"

# Display the image
st.image(image_path)
# Add sidebar links
with st.sidebar:
    for link in sidebar_links:
        st.page_link(link["path"], label=link["label"], icon=link["icon"])
        st.page_link(link["path"], label=link["label"], icon=link["icon"])
