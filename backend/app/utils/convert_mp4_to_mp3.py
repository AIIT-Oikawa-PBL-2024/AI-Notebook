import asyncio
import logging
import os

import ffmpeg
from google.cloud import storage

# ロギングの設定
logging.basicConfig(level=logging.INFO)


# MP4のファイルをMP3に変換してGCSに保存
async def convert_mp4_to_mp3(bucket_name: str, file_name: str) -> bool:
    # GCSからファイルを取得
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    mp4_base_name = os.path.basename(file_name)
    mp4_file_path = os.path.normpath(f"/tmp/{mp4_base_name}")
    if not mp4_file_path.startswith("/tmp/"):
        raise ValueError("Invalid file path")
    await asyncio.to_thread(blob.download_to_filename, mp4_file_path)

    # MP4ファイルをMP3に変換
    mp3_base_name = mp4_base_name.replace(".mp4", ".mp3")
    mp3_file_path = os.path.normpath(f"/tmp/{mp3_base_name}")
    if not mp3_file_path.startswith("/tmp/"):
        raise ValueError("Invalid file path")
    await asyncio.to_thread(
        lambda: ffmpeg.input(mp4_file_path)
        .output(mp3_file_path, format="mp3", acodec="libmp3lame")
        .run()
    )

    # MP3ファイルをGCSにアップロード
    upload_file_name = f'mp3/{file_name.replace(".mp4", ".mp3")}'
    mp3_blob = bucket.blob(upload_file_name)
    await asyncio.to_thread(mp3_blob.upload_from_filename, mp3_file_path)

    # 一時ファイルを削除
    await asyncio.to_thread(os.remove, mp4_file_path)
    await asyncio.to_thread(os.remove, mp3_file_path)

    # mp3_blob.exists() は同期的なので非同期にラップ
    return await asyncio.to_thread(mp3_blob.exists)
