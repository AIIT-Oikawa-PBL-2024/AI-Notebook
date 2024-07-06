#!/bin/bash
set -e

# DBのマイグレーションを実行
poetry run python -m app.migrate_cloud_db

# FastAPIサーバーを起動
poetry run uvicorn app.main:app --host 0.0.0.0
