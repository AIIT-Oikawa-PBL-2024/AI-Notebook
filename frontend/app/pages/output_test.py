## Issue No.2
## Title Input:画像入力インターフェース機能
##タスク1,3,4
##https://github.com/orgs/AIIT-Oikawa-PBL-2024/projects/9/views/1?sortedBy%5Bdirection%5D=asc&sortedBy%5BcolumnId%5D=108570462

## 概要
##AIサポート学習帳の画像アップロード画面
##ファイルタイプを'png', 'pdf', 'jpeg', 'jpg'に制限する
##ファイルサイズは‘.streamlit/config.toml’で変更（デフォルト200MB）

import os

import streamlit as st
from PIL import Image


IMG_PATH = 'imgs'

with st.sidebar:
    st.page_link("main.py", label="ホーム", icon="🏠")
    st.page_link("pages/upload_image.py", label="ファイルアップロード", icon="1️⃣")
    st.page_link("pages/input_text.py", label="テキスト入力", icon="2️⃣")
    st.page_link("pages/output_note.py", label="AIサポート学習帳", icon="3️⃣")
    st.page_link("pages/output_test.py", label="AIサポートテスト", icon="4️⃣")
    st.page_link("pages/flyer.py", label="PBL フライヤー")

def main():
    st.markdown('# AIサポート学習帳')
    file = st.file_uploader('講義テキストの画像をアップロードしてください.（アプロード可能なファイルタイプ：png,pdf,jpeg,jpg）', type=['png', 'pdf', 'jpeg', 'jpg'])
    if file:
        st.markdown(f'{file.name} をアップロードしました.')
        #img_path = os.path.join(IMG_PATH, file.name)
        # 画像を保存する
        #with open(img_path, 'wb') as f:
        #    f.write(file.read())
        #    
        # 保存した画像を表示
       # img = Image.open(img_path)
        #st.image(img)

if __name__ == '__main__':
    main()