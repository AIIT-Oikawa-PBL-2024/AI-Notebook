# AI-NoteBook frontend　
### GCP Cloud Runへのデプロイ用設定（すでに設定済みです）

`Cloud Run`デプロイ用の設定ファイルの追加
- `Dockerfile.cloud_frontend`を作成
    - デプロイ用にコピー範囲を`appディレクトリ`に限定
    - 起動ファイル`entrypoint.sh`をコピー
    - 起動コマンド`ENTRYPOINT ["bash", "entrypoint.sh"]`を設定

- `entrypoint.sh`を作成
    - Stremalitサーバを起動

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
- `cd frontend`
- `docker build -t gcr.io/<PJNAME>/<APPNAME>:latest --platform linux/amd64 \`
    `-f frontend/Dockerfile.cloud_frontend .`

### Artifact RegistryへのPUSH
- `docker push gcr.io/<PJNAME>/<APPNAME>:latest`

### Cloud Runへのデプロイ
- コンソールから設定（環境変数、シークレット、ダイレクトVPC、サービスアカウント権限）

### クライアント端末からの認証あり接続
- `gcloud run services proxy <APPNAME> --project <PJNAME>`
