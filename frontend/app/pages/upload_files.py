import os

import httpx  # Add this line
import streamlit as st

# ./PBLフライヤー1Q.jpg　を表示する
with st.sidebar:
    st.page_link("main.py", label="ホーム", icon="🏠")
    st.page_link("pages/upload_files.py", label="ファイルアップロード", icon="1️⃣")

# Constants
ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB in bytes


def is_valid_file(file):
    # Check file extension
    file_ext = os.path.splitext(file.name)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(
            f" {file.name}をアップロードできませんでした。PDF、JPG、JPEG、"
            "またはPNGファイルをアップロードしてください"
        )
        return False

    # Check file size
    if file.size > MAX_FILE_SIZE:
        st.error(
            f"{file.name}をアップロードできませんでした。200 MB以下のファイルを"
            "アップロードしてください。"
        )
        return False

    return True


def main():
    st.title("ファイルアップロード")

    uploaded_files = st.file_uploader("", accept_multiple_files=True)

    if uploaded_files:
        valid_files = []
        file_names = set()

        for file in uploaded_files:
            if file.name in file_names:
                st.warning(
                    f" {file.name}ファイルは既にアップロードされています。重複した"
                    "ファイルは登録されません。他のファイルをアップロードしてください。"
                )
                continue

            if is_valid_file(file):
                valid_files.append(file)
                file_names.add(file.name)
                st.success(
                    f"Valid file: {file.name} (Size: {file.size / 1024 / 1024:.2f} MB)"
                )

        if valid_files:
            if st.button("登録"):
                try:
                    with httpx.Client() as client:
                        files = {f.name: f.getvalue() for f in valid_files}
                        response = client.post("http://www.test.com", files=files)

                        if response.status_code == 200:
                            st.success("ファイルは正常に登録されました。")
                        else:
                            st.error(
                                f"ファイルは登録できませんでした。 Status code: {response.status_code}"
                            )
                except httpx.RequestError as e:
                    st.error(f" {e}リクエストでエラーが発生しました。")
        else:
            st.warning(
                "ファイルが登録されませんでした。 有効なファイルをアップロードしてください。"
            )


if __name__ == "__main__":
    main()
