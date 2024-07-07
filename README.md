# AI-Notebook

フロントエンドは Streamlit、バックエンドは FastAPI を利用

```
AI-Notebook
├── .devcontainer
│   └── backend
|   |     └── devcontainer.json
|   └── frontend
|         └── devcontainer.json
├── .github
│   └── workflows
|   |     └── pytest.yml
|   └── dependabot.yml
├── backend
│   ├── .vscode
│   │    └── settings.json
│   ├── app
│   │    ├── main.py
│   │    ├── database.py
│   │    ├── migrate_db.py
│   │    ├── cruds
│   │    ├── db ※マイグレーション（alembic_dev, alembic_test）
│   │    ├── models
│   │    ├── routers
│   │    ├── schemas
│   │    └── utils
│   ├── tests
│   ├── Dockerfile.backend
│   ├── Dockerfile.cloud_backend
│   ├── entrypoint.sh
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── README.md

├── frontend
│   ├── .vscode
│   │    └── settings.json
│   ├── app
│   │    └── main.py
│   ├── app.py
│   ├── tests
│   ├── Dockerfile.frontend
│   ├── Dockerfile.cloud_frontend
│   ├── entrypoint.sh
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── README.md
├── docker-compose.yml
├── .env.sample
├── .coderabbit.yaml
├── .gitignore
└── README.md
```

## プロジェクトの構成

- `.devcontainer`: バックエンドとフロントエンドで devcontainer.json を使い分け

### Backend

- `backend/app/`: FastAPI のコード用ディレクトリ

- `backend/tests/`: FastAPI のテストコード用ディレクトリ

- `backend/Dockerfile.backend`: バックエンドコンテナをビルドするための Dockerfile。ベースイメージを指定し、Poetry を使用して必要な依存関係をインストールし、アプリケーションコードをコンテナにコピーする。

- `backend/poetry.lock` and `backend/pyproject.toml`: Poetry によるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Frontend

- `frontend/app/`: Stremlit のコード用ディレクトリ

- `frontend/tests/`: Streamlit のテストコード用ディレクトリ

- `frontend/Dockerfile.forntend`: フロントエンドコンテナをビルドするための Dockerfile。ベースイメージを指定し、Poetry を使用して必要な依存関係をインストールし、アプリケーションコードをコンテナにコピー。

- `frontend/poetry.lock` and `frontend/pyproject.toml`: Poetry によるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Docker Compose

- `docker-compose.yml`: フロントエンド、バックエンド、DB のコンテナのサービス、公開するポートを定義する。

  ※DB には MySQL を利用する。

## 作成方法

- `git clone`でリポジトリをダウンロード
- ルートディレクトリにある`.env.sample`ファイルをコピーして、`.env`ファイルを作成

  DB の設定は変更せず、password はブランクのままにしてください。

  - `GOOGLE_APPLICATION_CREDENTIALS`に GCP サービスアカウントキーのファイルのパスを入力
  - `BUCKET_NAME`に GCP のバケット名を入力

- `$ docker compose build --no-cache`で Docker イメージをビルド
- `$ cd backend`
- `$ docker compose run --entrypoint "poetry install --no-root" backend`
- `$ cd ../frontend`
- `$ docker compose run --entrypoint "poetry install --no-root" frontend`
- `./backend/.env/`ディレクトリを作成して、ディレクトリ内にサービスアカウントキーを格納
- .env.sample ファイルを参考にして、.env ファイルに環境変数を追加
  - `GOOGLE_APPLICATION_CREDENTIALS=<サービスアカウントキーのファイルのパス>`
  - `PROJECT_ID=<PROJECT_ID>`
  - `REGION="asia-northeast1"`
  - `BUCKET_NAME=<BUCKET_NAME>`
- backend のコンテナ内で`gcloud auth login --cred-file=<サービスアカウントキーのファイルのパス>`
- パッケージ管理は poetry を使用

  　 backend と frontend のそれぞれの定義ファイルからインストール

  `$ cd backend`

  `$ docker compose run --entrypoint "poetry install --no-root" backend`

  `$ cd ../frontend`

  `$ docker compose run --entrypoint "poetry install --no-root" frontend`

- `pyproject.toml`ファイルをもとに`.venv`ディレクトリにパッケージがインストールされる。

- ルートディレクトリから`$ docker compose up`でコンテナを立ち上げ
- エラーが出る場合は、`$ docker compose build --no-cache`で Docker イメージを再度ビルドしてみる。

- ブラウザから動作確認 8000 番ポートに FastAPI、8501 番ポートに Streamlit が立ち上がる

- Dev Container の起動確認 VSCode 左下の「><」マークから「コンテナで再度開く」を選択

  backend, frontend のコンテナ内で操作できる。

- DB の起動確認

  - 開発用 DB
    - `$ docker compose exec dev-db mysql dev-db`で起動
  - テスト用 DB
    - `$ docker compose exec test-db mysql test-db`で起動

- DB マイグレーション(backend の DevContainer 内で実行)
  - 開発用 DB
    - `$ cd app/db/alembic_dev`
    - `$ alembic upgrade head`
    - [エラーが出る場合はドキュメント確認](https://alembic.sqlalchemy.org/en/latest/tutorial.html#running-our-first-migration)
  - テスト用 DB

    テスト用 DBについてはalembicコマンドは実行しない

    理由はテストコードの中で毎回テーブルを作成して、削除しているため、alembicコマンドと併用すると不整合が起きるため
  
- テーブル作成の確認

  - `$ docker compose exec dev-db mysql dev-db`
  - `mysql> SHOW TABLES;`
  - `mysql> DESCRIBE users;`

- DB マイグレーション実施後は、
  
  FastAPI の Swagger UI から DB にアクセス可能になる。
  
  8000 番ポートの`/docs`パスで確認

- Google VertexAI のローカル環境での利用方法

  - GCP でサービスアカウントキーの作成
  - `./backend/.env/`ディレクトリを作成して、ディレクトリ内にサービスアカウントキーを格納
    - **重要**　**ファイル名がグレーアウトされていて、GitHub に上がらないことを確認**
  
  - .env.sample ファイルを参考にして、.env ファイルに環境変数を追加
    - `GOOGLE_APPLICATION_CREDENTIALS=<サービスアカウントキーのファイルのパス>`
    - `PROJECT_ID=<PROJECT_ID>`
    - `REGION="asia-northeast1"`
    - `BUCKET_NAME=<BUCKET_NAME>`
  - Docker イメージのリビルド `$ docker compose build --no-cache`
  - backend のコンテナ内で`gcloud auth login --cred-file=<サービスアカウントキーのファイルのパス>`
    - 以下の表示が出るが PROJECT_ID は設定しない
      - `Your current project is [None].  You can change this setting by running:`
      - `$ gcloud config set project PROJECT_ID`

  - backend のコンテナ内で`sudo poetry install --no-root` ※google 関連パッケージを sudo 権限でインストール
  - `python app/utils/gemini_request_stream.py`で gemini から出力されれば OK

- パッケージを追加する場合
  - Dev Container を起動してから`$ poetry add <パッケージ>`
  - 開発環境のみのパッケージは`$ poetry add -D <パッケージ>`

  - ローカル環境から操作したい場合
    - バックエンド `$ docker compose exec backend poetry add <パッケージ>`
    - フロントエンド `$ docker compose exec frontend poetry add <パッケージ>`

## 設定ファイル

- .gitignore ファイル
  - 以下のファイルをコピーして、カスタマイズ
  - https://github.com/github/gitignore/blob/main/Python.gitignore

- .coderabbit.yaml ファイル
  - コードラビットの設定ファイル

- .vscode/settings.json
  - リンター、フォーマッターとして ruff, mypy を設定
  - `pyproject.tomlにも[tool.ruff],[tool.mypy]を設定済み`
  - ⭐️VSCode の拡張機能でも ruff と mypy をインストール

## テストの実行

- Dev Container での実行
  - `pytest tests/ --cov=app`

- GitHub Actions の CI 実行
  - 実行ファイル
    - `.github/workflows/pytest.yml`
      - `backend`, `frontend`で処理を分けています。
      - `coverage-path-prefix`を設定することで、リンクのパスに飛ぶようになりました。

  - GitHub Actions の処理について
    - Ruff, Mypy, Pytest が実行されます。
  - 参考ページ
    - https://github.com/MishaKav/pytest-coverage-comment
