# frontrnd-nextjsディレクトリを設定する方法
- `AI-Notebook`のGitHubリポジトリからローカルにプル
- ローカル環境にnpmがインストールされていることを確認
- `npm -v`と`node -v`を実行してバージョン表示（表示されない場合はインストール）
- pnpmのインストール `npm install -g pnpm`
- ディレクトリ移動 `cd frontend-nectjs`
- パッケージインストール`pnpm install`
- ルートディレクトリに移動 `cd ..`
- Dockerイメージ作成 `docker compose build`
- Dockerコンテナ起動 `docker compose up`

# 環境変数の設定
- `frontend-nextjs`フォルダ内の`.env.local.sample`をコピーして、`.env.local`を作成
- [firebaseのコンソール](https://console.firebase.google.com/)を開く
- アプリAI-Notebookの設定を開いて、「SDK の設定と構成」のConfigをコピー
- 環境変数として`firebase`の`config`から追記　


# （参考）Next.jsディレクトリをゼロから　設定する方法
- AI-Notebookのディレクトリ内にfrontend-nextjsディレクトリを作成する設定

## PCにnpmのインストール（LTSのv20を選択）
- [Node.jsのダウンロードページ](https://nodejs.org/en/download/package-manager)
- VSCodeでAI-Notebookeフォルダを開く
- ターミナルでインストール済みのバージョン確認
- `npm -v`
- `node -v`

## pnpmのインストール
- `npm install -g pnpm`

## Next.jsインストール
- `npx create-next-app@latest --use-pnpm`

対話型で進む
```
✔ What is your project named? … frontend-nextjs
✔ Would you like to use TypeScript? … Yes
✔ Would you like to use ESLint? … No
✔ Would you like to use Tailwind CSS? … Yes
✔ Would you like to use `src/` directory? … No 
✔ Would you like to use App Router? (recommended) …  Yes
✔ Would you like to customize the default import alias (@/*)? … No 
```

起動確認
`cd frontend-nextjs`
`pnpm run dev`
```
▲ Next.js 14.2.13
  - Local:        http://localhost:3000
URLクリックでブラウザ起動
```

## Dockerコンテナの設定
- `./frontend-nextjs/Dockerfile.frontend-nextjs`のファイル作成
- `./docker-compose.yml`にサービス追加

- ターミナルでコンテナ起動確認
- `docker compose up`
```
nextjs http://localhost:3000/
Backend http://localhost:8000/
Streamlit http://localhost:8501/
CTRL+Cで停止
```

## devcontainer設定
`.devcontainer/frontend-nextjs/devcontainer.json`　ファイルを作成
  - `docker-compose.yml`をベースに `VS Code` の `devcontainer` を設定
  - コンテナ内に拡張機能として`es7-react`と`biome`を導入
  - 起動時に`pnpm install`を実行して、ライブラリを再導入

- VSCode拡張機能の設定
- `frontend-nextjs/.vscode/extensions.json`
- `frontend-nextjs/.vscode/settings.json`

- devcontainerの確認
- VSCodeの左下><をクリック　コンテナで再度開く
- `frontend-nextjs-dev-container`を選択
- コンテナ内からも`pnpm run dev`を実行できる

## Biomeの導入
- `cd frontend-nextjs`
- `pnpm add --save-dev --save-exact @biomejs/biome`
- `pnpm biome init`
- `biom.json`　対象ファイルを指定

- 試しにフォーマット実行（CLIでフォーマット） `pnpm check`　または　`pnpm biome check`
- VSCodeのファイル保存でもフォーマット可能になる

- `biome`が動かない場合
- すべてのバイナリをインストール
- `pnpm install --save-dev --force @biomejs/cli-darwin-arm64 @biomejs/cli-darwin-x64 @biomejs/cli-linux-arm64 @biomejs/cli-linux-x64 @biomejs/cli-win32-arm64 @biomejs/cli-win32-x64`

## vitestの導入
[vitestの設定ドキュメント](https://nextjs.org/docs/app/building-your-application/testing/vitest)
- `cd frontend-nextjs`
- `pnpm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom`
- `pnpm install -D @vitest/coverage-v8`
- `vitest.config.ts`を追加
- `package.json`への設定追加

## テストファイル作成  `__tests__/page.test.ts`
- テスト実行 `pnpm test`　または　`pnpm vitest run`
- ガバレッジ出力 `pnpm vitest run --coverage`でテストカバレッジ出力

## CIの設定
- `.github/workflows/pytest.yml`　→　`.github/workflows/ci.yml`に名前変更 
- `vitest.config.ts`にカバレッジレポートの設定を追加

## 手動でCloud Runへのデプロイ
- 開発用の環境変数`.env.development.local`と本番用の環境変数`.env.production.local`をサンプルファイルから作成
- 手動デプロイ用のDockerコンテナをビルドしてプッシュ
  - `cd frontend-nextjs`
  - `docker build -t gcr.io/<PROJECT-ID>/<APP-NAME> --platform linux/amd64 -f Dockerfile.gcloud-nextjs .`
  - `docker push gcr.io/<PROJECT-ID>/<APP-NAME>`
- Cloud Run コンソールで「新しいリビジョンの編集とデプロイ」→「コンテナイメージ」を選択
