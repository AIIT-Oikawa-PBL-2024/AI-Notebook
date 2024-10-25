// features/file/SelectFiles.tsx
'use client'

import { useState } from 'react';
import { Button } from '@material-tailwind/react';

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_DEV_API_URL = `${BACKEND_HOST}/files/`;
const BACKEND_DELETE_API_URL = `${BACKEND_HOST}/files/delete_files`;

interface FileData {
  id: number;
  user_id: number;
  file_name: string;
  file_size: number;
  created_at: string;
  select: boolean;
}

export function SelectFiles() {
  const [files, setFiles] = useState<FileData[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 時刻フォーマットを変換する関数
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr.replace('Z', '+00:00'));
    return date.toLocaleString('ja-JP');
  };

  // ファイル一覧を取得する関数
  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(BACKEND_DEV_API_URL, {
        headers: { accept: 'application/json' }
      });
      if (!response.ok) throw new Error('ファイル一覧の取得に失敗しました');
      const data = await response.json();
      const formattedData = data.map((file: FileData) => ({
        ...file,
        created_at: formatTime(file.created_at),
        select: false
      }));
      setFiles(formattedData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '予期せぬエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  // ファイルの選択を処理する関数
  const handleFileSelect = (fileName: string, selected: boolean) => {
    setFiles(files.map(file => 
      file.file_name === fileName ? { ...file, select: selected } : file
    ));
    setSelectedFiles(prev => 
      selected 
        ? [...prev, fileName]
        : prev.filter(f => f !== fileName)
    );
  };

  // ファイルを削除する関数
  const handleDeleteFiles = async () => {
    if (selectedFiles.length === 0) {
      setError('削除するファイルを選択してください');
      return;
    }

    try {
      const response = await fetch(`${BACKEND_DELETE_API_URL}?user_id=1`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          accept: 'application/json'
        },
        body: JSON.stringify(selectedFiles)
      });

      const result = await response.json();
      if (result.success) {
        await fetchFiles();
        setSelectedFiles([]);
        setError(null);
        // 成功メッセージを表示
      } else {
        setError(result.detail || 'ファイルの削除に失敗しました');
      }
    } catch (err) {
      setError('エラーが発生しました');
    }
  };

  // リセット処理
  const handleReset = () => {
    setFiles([]);
    setSelectedFiles([]);
    setTitle('');
    setError(null);
  };

  // AIノート作成処理
  const handleCreateNote = async () => {
    if (!title || selectedFiles.length === 0) return;
    const router = useRouter();
    router.push(
      `/notebooks/create?title=${encodeURIComponent(title)}&files=${encodeURIComponent(JSON.stringify(selectedFiles))}`
    );
  };

  // AI練習問題作成処理
  const handleCreateExercise = async () => {
    if (!title || selectedFiles.length === 0) return;
    const router = useRouter();
    router.push(
      `/exercises/create?title=${encodeURIComponent(title)}&files=${encodeURIComponent(JSON.stringify(selectedFiles))}`
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <Button
          onClick={fetchFiles}
          disabled={loading}
          className="bg-blue-500"
        >
          ファイル一覧を取得
        </Button>
        <Button
          onClick={handleReset}
          className="bg-gray-500"
        >
          リセット
        </Button>
        <Button
          onClick={handleDeleteFiles}
          disabled={selectedFiles.length === 0}
          className="bg-red-500"
        >
          選択したファイルを削除
        </Button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <FileList
        files={files}
        onFileSelect={handleFileSelect}
        loading={loading}
      />

      {selectedFiles.length > 0 && (
        <div className="space-y-6 mt-8">
          <div>
            <h3 className="text-lg font-bold text-blue-800 mb-2">選択されたファイル</h3>
            <div className="p-4 bg-gray-50 rounded">
              {selectedFiles.map(file => (
                <div key={file} className="mb-1">{file}</div>
              ))}
            </div>
          </div>

          <div className="border-t pt-6">
            <h3 className="text-lg font-bold text-blue-800 mb-4">タイトル</h3>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="AIで作成するノートや練習問題のタイトルを100文字以内で入力してEnterキーを押して下さい"
              maxLength={100}
              className="w-full p-2 border rounded focus:outline-none focus:border-blue-500"
            />
            {title && (
              <p className="mt-2 text-gray-600">
                Title: {title}
              </p>
            )}
          </div>

          {title && (
            <div className="space-y-4">
              <Button
                onClick={handleCreateNote}
                className="w-full bg-blue-500"
              >
                AIノートを作成
              </Button>
              <Button
                onClick={handleCreateExercise}
                className="w-full bg-green-500"
              >
                AI練習問題を作成
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}