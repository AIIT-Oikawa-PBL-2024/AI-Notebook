# AI-NoteBook backend　

### Backend の 構築方法
- パッケージ管理は poetry を使用
- `$ cd backend`
- `$ docker compose run --entrypoint "poetry install --no-root" backend`
- `pyproject.toml`ファイルをもとに`.venv`ディレクトリにパッケージがインストールされる。
- `./backend/env/`ディレクトリを作成して、ディレクトリ内にサービスアカウントキーを格納
- ルートディレクトリから`$ docker compose up`でコンテナを立ち上げ
- エラーが出る場合は、`$ docker compose build --no-cache`で Docker イメージを再度ビルドしてみる。
- ブラウザから動作確認 8000 番ポートに FastAPIが立ち上がる
- Dev Container の起動確認 VSCode 左下の「><」マークから「コンテナで再度開く」を選択

  backendのコンテナ内で操作できる。

  - Dev Containerを使用せず、ターミナルからコンテナ内に入る場合
    - `docker compose exec backend bash` 
    - `CTRL + D` で終了

- DB の起動確認
  - 開発用 DB
    - `$ docker compose exec dev-db mysql dev-db`で起動
  - テスト用 DB
    - `$ docker compose exec test-db mysql test-db`で起動

- DB マイグレーション(backend の DevContainer 内で実行)
  - 開発用 DB
  - `$ cd app/db/alembic_dev`
  - 新たにテーブルを作成した場合`app/db/alembic_dev/env.py`と`app/migrate_cloud_db.py`にテーブルのモデルを追加
  - マイグレーションスクリプトを生成`alembic revision --autogenerate -m "add XXXX table"`  
  - マイグレーション適用`$ alembic upgrade head`
    - alimbicコマンドがうまく実行されない場合は'poetry run alembic upgrade head'を実行
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
  - `./backend/env/`ディレクトリを作成して、ディレクトリ内にサービスアカウントキーを格納
    - **重要**　**ファイル名がグレーアウトされていて、GitHub に上がらないことを確認**
  
  - .env.sample ファイルを参考にして、.env ファイルに環境変数を追加したことを確認
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

### 設定ファイル
- .vscode/settings.json
  - リンター、フォーマッターとして ruff, mypy を設定
  - `pyproject.tomlにも[tool.ruff],[tool.mypy]を設定済み`
  - ⭐️VSCode の拡張機能でも ruff と mypy をインストール

### テストの実行
- Dev Container での実行
  - `pytest tests/ --cov=app`

### GCP Cloud Runへのデプロイ用設定
`Cloud Run`デプロイ用の設定ファイルの追加
- `Dockerfile.cloud_backend`を作成
    - デプロイ用にコピー範囲を`appディレクトリ`に限定
    - 起動ファイル`entrypoint.sh`をコピー
    - 起動コマンド`ENTRYPOINT ["bash", "entrypoint.sh"]`を設定

- `entrypoint.sh`を作成
    - DBマイグレーションを実行後、FastAPIサーバを起動

- `migrate_cloud_db.py`DBマイグレーションファイルを作成
    - DBの存在確認してからDB作成、テーブル作成

### サービスアカウントの作成と権限付与
- Google Cloud Build API を有効化
    - `gcloud services enable cloudbuild.googleapis.com`
- Google Cloud Run API を有効化
    - `gcloud services enable run.googleapis.com`
- サービスアカウントの作成
    - `gcloud iam service-accounts create <SANAME> \`
        `--display-name="<SANAME>"`
- Cloud Run起動権限
    - `gcloud projects add-iam-policy-binding <PJNAME> \`
        `--member="serviceAccount:<SANAME>@<PJNAME>.iam.gserviceaccount.com" \`
        `--role="roles/run.invoker"`
- サービス利用権限
    - `gcloud projects add-iam-policy-binding <PJNAME> \`
        `--member="serviceAccount:<SANAME>@<PJNAME>.iam.gserviceaccount.com" \`
        `--role="roles/serviceusage.serviceUsageConsumer"`
- Cloud Run管理権限
    - `gcloud projects add-iam-policy-binding <PJNAME> \`
        `--member="serviceAccount:<SANAME>@<PJNAME>.iam.gserviceaccount.com" \`
        `--role="roles/run.admin"`

### Dockerイメージの作成
- `cd backend`
- `docker build -t gcr.io/<PJNAME>/<APPNAME>:latest --platform linux/amd64 \`
    `-f Dockerfile.cloud_backend .`

### Artifact RegistryへのPUSH
- `docker push gcr.io/<PJNAME>/<APPNAME>:latest`

### DBの設定
- GCPコンソールからSQLインスタンス(MySQL)を作成

### Cloud Runへのデプロイ
- コンソールから設定（環境変数、シークレット、ダイレクトVPC、サービスアカウント権限）