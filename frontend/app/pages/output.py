import streamlit as st  # type: ignore


def get_output_raw_data() -> None:
    # TODO: アウトプットデータの仕様確認後進める
    pass

def convert_output_to_markdown() -> None:
    # TODO: 同上
    pass

def show_output_markdown(markdown_text: str = "**テストです**") -> None:
    st.markdown(markdown_text)


if __name__ == "__main__":
    show_output_markdown()
