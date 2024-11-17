# AI-Notebook

フロントエンドは Next.js、バックエンドは FastAPI を利用

```
AI-Notebook
├── .devcontainer
│   └── backend
|   |     └── devcontainer.json
|   └── frontend-nextjs
|         └── devcontainer.json
├── .github
│   └── workflows
|   |     └── ci.yml
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
├── frontend-nextjs
│   ├── __tests__
│   ├── .next
│   ├── .pnpm-store
│   ├── .vscode
│   │    └── settings.json
│   ├── node_modules
│   ├── public
│   ├── src
│   │    ├── app
│   │    ├── components
│   │    ├── features
│   │    ├── hooks
│   │    ├── providers
│   │    └── utils
│   ├── .env.development.local
│   ├── .env.local
│   ├── .env.production.local
│   ├── .gitigore
│   ├── biome.json
│   ├── cloudbuild.yaml
│   ├── Dockerfile
│   ├── Dockerfile.frontend-nextjs
│   ├── Dockerfile.gclous-nextjs
│   ├── next-env.d.ts
│   ├── next.config.mjs
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── postcss.config.mjs
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── vitest.config.ts
│   ├── vitest.setup.ts
│   └── README.md
├── docker-compose.yml
├── .coderabbit.yaml
├── .gitignore
└── README.md
```

## プロジェクトの構成
- `.devcontainer`: バックエンドとフロントエンドで devcontainer.json を使い分け

### Backend
- `backend/app/`: FastAPI のコード用ディレクトリ
- `backend/tests/`: FastAPI のテストコード用ディレクトリ
- `backend/Dockerfile.backend`: バックエンド開発用の Dockerfile
- `backend/Dockerfile.cloud_backend`: バックエンドのCloud Runデプロイ用の Dockerfile
- `backend/poetry.lock` and `backend/pyproject.toml`: Poetry によるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Frontend
- `frontend-nextjs/src/`: Next.js のコード用ディレクトリ
- `frontend-nextjs/__tests__/`: Next.js のテストコード用ディレクトリ
- `frontend-nextjs/Dockerfile`: フロントエンドのCloud Build　継続的デプロイ用 Dockerfile
- `frontend-nextjs/Dockerfile.forntend-nextjs`: フロントエンド開発用 Dockerfile
- `frontend-nextjs/Dockerfile.gcloud-nextjs`: フロントエンドのCloud Run 手動デプロイ用 Dockerfile
- `frontend-nextjs/package.json` and `frontend-nextjs/pnpm-lock.yaml`: pnpm によるパッケージ管理ファイル。プロジェクトの依存関係とそのバージョンを指定する。

### Docker Compose
- `docker-compose.yml`: フロントエンド、バックエンド、DB のコンテナのサービス、公開するポートを定義する。

  ※DB には MySQL を利用する。

## 作成方法
- `git clone`でリポジトリをダウンロード
- `backend`と`frontend-nextjs`ディレクトリにある`.env.sample`ファイルをコピーして、`.env`ファイルを作成

  DB の設定は変更せず、password はブランクのままにしてください。

  - `GOOGLE_APPLICATION_CREDENTIALS`に GCP サービスアカウントキーのファイルのパスを入力
  - `PROJECT_ID`にGCPのプロジェクトIDを入力
  - `BUCKET_NAME`に GCP のバケット名を入力

- `$ docker compose build --no-cache`で Docker イメージをビルド

## 設定ファイル
- .gitignore ファイル
  - 以下のファイルをコピーして、カスタマイズ
  - https://github.com/github/gitignore/blob/main/Python.gitignore
- .coderabbit.yaml ファイル
  - コードラビットの設定ファイル

## テストの実行
- GitHub Actions の CI 実行
  - 実行ファイル
    - `.github/workflows/ci.yml`
      - `backend`, `frontend-nextjs`で処理を分けています。

  - GitHub Actions の処理について
    - `backend` Ruff, Mypy, Pytest が実行されます。
    - `frontend-nextjs` Biome, Vitestが実行されます。
  - 参考ページ
    - https://github.com/MishaKav/pytest-coverage-comment

## FIREBASEの設定
- バックエンド側
  - [firebaseのコンソール](https://console.firebase.google.com/)を開く
  - 「プロジェクトの設定」->「サービスアカウント」->「新しい秘密鍵を生成」
  - バックエンドフォルダ内の任意の場所に秘密鍵を保存して、.envに秘密鍵のパスを指定
    - `FIREBASE_CREDENTIALS=<FirebaseAdminSDKキーJSONファイルへのパス>`
- フロントエンド側
  - `frontend-nextjs`フォルダ内の`.env.local.sample`をコピーして、`.env.local`を作成
  - [firebaseのコンソール](https://console.firebase.google.com/)を開く
  - アプリAI-Notebookの設定を開いて、「SDK の設定と構成」のConfigをコピー
  - 環境変数として`firebase`の`config`から追記　

## 署名付きURLを利用してアップロードする場合はCORSの設定を行う必要がある
- 開発環境については設定済
- 本番環境については以下の手順で設定を行う必要がある
  - backendのコンテナから現在のcors設定を確認する
　- `gsutil cors get gs://BUCKET_NAME`
  - 設定内容に基づいてjsonファイルを作成して、以下のコマンドcorsの設定を行う
  - `gcloud storage buckets update gs://BUCKET_NAME --cors-file=JSON_FILE`