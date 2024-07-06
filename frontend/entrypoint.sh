#!/bin/bash
set -e

# Streamlitサーバーを起動
poetry run streamlit run app/main.py --server.port 8501 --server.address 0.0.0.0
