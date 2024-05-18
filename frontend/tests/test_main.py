from dotenv import load_dotenv
from streamlit.testing.v1 import AppTest

# 環境変数を読み込む
load_dotenv()


# モックデータ
mock = {"message": "Hello World"}


def test_main():
    "Test the main function of the app."
    at = AppTest.from_file("app/main.py").run()
    assert at.title[0].value == "Frontend App"
    assert (
        at.markdown[0].value
        == "This is a frontend application that communicates with a backend service."
    )
    assert at.button[0].label == "Submit"
    assert at.text_input[0].label == "何か書いて"
    assert at.text_input[0].value == ""
