# AI-NoteBook-template
フロントエンドはStreamlit、バックエンドはFastAPIを利用
```
copilot-practice2
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
│   ├── poetry.lock
│   └── pyproject.toml
├── frontend
│   ├── .vscode
│   │    └── settings.json
│   ├── app
│   │    └── main.py
│   ├── app.py
│   ├── tests
│   ├── Dockerfile.frontend
│   ├── poetry.lock
│   └── pyproject.toml
├── docker-compose.yml
├── .env.sample
├── .coderabbit.yaml
├── .gitignore
└── README.md
```

## プロジェクトの構成

- `.devcontainer`: バックエンドとフロントエンドでdevcontainer.jsonを使い分け

### Backend

- `backend/app/`: FastAPIのコード用ディレクトリ

- `backend/tests/`: FastAPIのテストコード用ディレクトリ

- `backend/Dockerfile.backend`: バックエンドコンテナをビルドするためのDockerfile。ベースイメージを指定し、Poetryを使用して必要な依存関係をインストールし、アプリケーションコードをコンテナにコピーする。

- `backend/poetry.lock` and `backend/pyproject.toml`: Poetryによるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Frontend

- `frontend/app/`: Stremlitのコード用ディレクトリ

- `frontend/tests/`: Streamlitのテストコード用ディレクトリ

- `frontend/Dockerfile.forntend`: フロントエンドコンテナをビルドするためのDockerfile。ベースイメージを指定し、Poetryを使用して必要な依存関係をインストールし、アプリケーションコードをコンテナにコピー。

- `frontend/poetry.lock` and `frontend/pyproject.toml`: Poetryによるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Docker Compose

- `docker-compose.yml`: フロントエンド、バックエンド、DBのコンテナのサービス、公開するポートを定義する。<br>
※DBにはMySQLを利用する。

## 作成方法
- `git clone`でリポジトリをダウンロード
- ルートディレクトリにある`.env.sample`ファイルをコピーして、`.env`ファイルを作成<br>
  DB の設定は変更せず、password はブランクのままにしてください。<br>
  - `GOOGLE_APPLICATION_CREDENTIALS_JSON`に GCP サービスアカウントキーのファイルのパスを入力
  - `BUCKET_NAME`に GCP のバケット名を入力
- `$ docker compose build --no-cache`でDockerイメージをビルド
- パッケージ管理はpoetryを使用<br>
　backendとfrontendのそれぞれの定義ファイルからインストール<br>
   `$ cd backend`
   `$ docker compose run --entrypoint "poetry install --no-root" backend`<br>
   `$ cd ../frontend`
   `$ docker compose run --entrypoint "poetry install --no-root" frontend`<br>
- `pyproject.toml`ファイルをもとに`.venv`ディレクトリにパッケージがインストールされる。

- ルートディレクトリから`$ docker compose up`でコンテナを立ち上げ
- エラーが出る場合は、`$ docker compose build --no-cache`でDockerイメージを再度ビルドしてみる。

- ブラウザから動作確認 8000番ポートにFastAPI、8501番ポートにStreamlitが立ち上がる

- Dev Containerの起動確認 VSCode左下の「><」マークから「コンテナで再度開く」を選択
   backend, frontendのコンテナ内で操作できる。

- DBの起動確認
   - 開発用DB
      - `$ docker compose exec dev-db mysql dev-db`で起動
   - テスト用DB
      - `$ docker compose exec test-db mysql test-db`で起動

- DB マイグレーション(backend の DevContainer 内で実行)
  - 開発用 DB
    - `$ cd app/db/alembic_dev`
    - エラーが出る場合は最新のマイグレーションファイルを削除
      - (`/backend/app/db/alembic_dev/versions/828f9c90de2f_dev_migration.py`があれば削除)
    - `$ alembic upgrade head`
    - マイグレーションできることを確認
    - `$ alembic revision --autogenerate -m "dev migration`
    - `$ alembic upgrade head`
  - テスト用 DB
    - `$ cd app/db/alembic_test`
    - エラーが出る場合は最新のマイグレーションファイルを削除
      - (`/backend/app/db/alembic_test/versions/a53b2fedf2e7_test_migration.py`があれば削除)
    - マイグレーションできることを確認
    - `$ alembic revision --autogenerate -m "test migration"`
    - `$ alembic upgrade head`
  
- テーブル作成の確認
   - `$ docker compose exec dev-db mysql dev-db`
   - `mysql> SHOW TABLES;`
   - `mysql> DESCRIBE users;`

- DBマイグレーション実施後は、
   FastAPIのSwagger UIからDBにアクセス可能になる。
   8000番ポートの`/docs`パスで確認

- パッケージを追加する場合
   - Dev Containerを起動してから`$ poetry add <パッケージ>`
   - 開発環境のみのパッケージは`$ poetry add -D <パッケージ>`
   
   ※ローカル環境から操作したい場合
   - バックエンド `$ docker compose exec backend poetry add <パッケージ>`
   - フロントエンド `$ docker compose exec frontend poetry add <パッケージ>`

## 設定ファイル
- .gitignoreファイル<br>
以下のファイルをコピーして、カスタマイズ<br>
https://github.com/github/gitignore/blob/main/Python.gitignore

- .coderabbit.yamlファイル<br>
コードラビットの設定ファイル

- .vscode/settings.json<br>
リンター、フォーマッターとしてruff, mypyを設定<br>
`pyproject.tomlにも[tool.ruff],[tool.mypy]を設定済み`<br>
⭐️VSCodeの拡張機能でもruffとmypyをインストール

## テストの実行
- Dev Containerでの実行
   `pytest tests/ --cov=app`

- GitHub ActionsのCI実行
   - 実行ファイル
      `.github/workflows/pytest.yml`<br>
      `backend`, `frontend`で処理を分けています。
      `coverage-path-prefix`を設定することで、リンクのパスに飛ぶようになりました。

   - GitHub Actionsの処理について
      - Ruff, Mypy, Pytestが実行されます。
      参考ページ
      https://github.com/MishaKav/pytest-coverage-comment
