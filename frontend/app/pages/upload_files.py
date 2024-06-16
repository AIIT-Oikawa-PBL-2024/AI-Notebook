import os

import httpx  # Add this line
import streamlit as st

# ./PBLフライヤー1Q.jpg　を表示する
with st.sidebar:
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/upload_files.py", label="Upload Files", icon="1️⃣")

# Constants
ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"]
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB in bytes


def is_valid_file(file):
    # Check file extension
    file_ext = os.path.splitext(file.name)[1][1:].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        st.error(
            f"Cannot upload {file.name}. Only PDF, JPG, JPEG, and PNG files are allowed."
        )
        return False

    # Check file size
    if file.size > MAX_FILE_SIZE:
        st.error(f"Cannot upload {file.name}. File size must be less than 200 MB.")
        return False

    return True


def main():
    st.title("Upload Files")

    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

    if uploaded_files:
        valid_files = []
        file_names = set()

        for file in uploaded_files:
            if file.name in file_names:
                st.warning(
                    f"Skipping {file.name}. This file has already been uploaded."
                )
                continue

            if is_valid_file(file):
                valid_files.append(file)
                file_names.add(file.name)
                st.success(
                    f"Valid file: {file.name} (Size: {file.size / 1024 / 1024:.2f} MB)"
                )

        if valid_files:
            if st.button("Submit"):
                try:
                    with httpx.Client() as client:
                        files = {f.name: f.getvalue() for f in valid_files}
                        response = client.post("http://www.test.com", files=files)

                        if response.status_code == 200:
                            st.success("Files successfully uploaded!")
                        else:
                            st.error(
                                f"Error occurred. Status code: {response.status_code}"
                            )
                except httpx.RequestError as e:
                    st.error(f"An error occurred during the request: {e}")
        else:
            st.warning(
                "No valid files to submit. Please upload PDF, JPG, JPEG, or PNG files (max 200 MB each)."
            )


if __name__ == "__main__":
    main()
