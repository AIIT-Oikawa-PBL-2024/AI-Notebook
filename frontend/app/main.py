import os

import requests
import streamlit as st
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

BACKEND_HOST = os.getenv("BACKEND_HOST")

st.title("Frontend App")

st.markdown("This is a frontend application that communicates with a backend service.")


def submit():
    if st.button("Submit"):
        try:
            response = requests.get(BACKEND_HOST)
            message = response.json()
            st.text(message["message"])
        except Exception as e:
            st.text("An error occurred.")
            st.text(e)


def wtite_message():
    message = st.text_input("何か書いて")
    st.write("あなたが書いたメッセージは: ", message)


def main():
    submit()
    wtite_message()


if __name__ == "__main__":
    main()
