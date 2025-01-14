#!/bin/bash
set -e

# DBのマイグレーションを実行
poetry run python -m app.migrate_cloud_db

# FastAPIサーバーを起動(ワーカー数は4)
poetry run hypercorn app.main:app --bind 0.0.0.0 --workers 4