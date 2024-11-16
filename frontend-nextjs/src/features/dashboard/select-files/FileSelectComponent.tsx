"use client";

import FileTable from "@/features/dashboard/select-files/FileTableComponent";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import {
	Alert,
	Button,
	Card,
	CardBody,
	CardHeader,
	Input,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_FILES = `${BACKEND_HOST}/files/`;
const BACKEND_API_URL_DELETE_FILES = `${BACKEND_HOST}/files/delete_files`;

interface FileData {
	file_name: string;
	file_size: string;
	created_at: string;
	select?: boolean;
	id?: string;
	user_id?: string;
}

// 選択問題関連のキャッシュキーを定数として定義
const CACHE_KEYS = {
	MULTI_CHOICE: {
		QUESTION: "cached_multi_choice_question",
		GENERATION_STATUS: "multi_choice_generation_status",
		ANSWERS: "cached_answers",
		RESULTS: "cached_results_state",
	},
	STREAM_EXERCISE: {
		EXERCISE: "cached_exercise",
		GENERATION_STATUS: "exercise_generation_status",
	},
};

export default function FileSelectComponent() {
	const router = useRouter();
	const { user, error: authError, clearError, reAuthenticate } = useAuth();
	const [files, setFiles] = useState<FileData[]>([]);
	const [title, setTitle] = useState("");
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState("");
	const authFetch = useAuthFetch();

	const handleAuthError = useCallback(
		async (error: { message: string }) => {
			if (error.message.includes("token") || error.message.includes("認証")) {
				await reAuthenticate();
			}
			setError(error.message);
		},
		[reAuthenticate],
	);

	const formatDate = useCallback((dateStr: string) => {
		return new Date(dateStr).toLocaleString();
	}, []);

	const fetchFiles = useCallback(async () => {
		if (!user) {
			setError("認証が必要です");
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(BACKEND_API_URL_GET_FILES);

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "ファイルの取得に失敗しました");
			}

			const data = await response.json();
			setFiles(data.map((file: FileData) => ({ ...file, select: false })));
			clearError();
		} catch (err: unknown) {
			await handleAuthError(err as { message: string });
		} finally {
			setLoading(false);
		}
	}, [user, clearError, handleAuthError, authFetch]);

	const deleteSelectedFiles = useCallback(async () => {
		if (!user) {
			setError("認証が必要です");
			return;
		}

		const selectedFiles = files
			.filter((file) => file.select)
			.map((file) => file.file_name);
		if (selectedFiles.length === 0) {
			setError("削除するファイルを選択してください");
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(BACKEND_API_URL_DELETE_FILES, {
				method: "DELETE",
				headers: {
					Accept: "application/json",
					"Content-Type": "application/json",
				},
				body: JSON.stringify(selectedFiles),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "ファイルの削除に失敗しました");
			}

			const result = await response.json();
			if (result.success) {
				setSuccess("選択したファイルを削除しました");
				await fetchFiles();
				clearError();
			} else {
				setError(
					result.failed_files?.length
						? `削除に失敗したファイル: ${result.failed_files.join(", ")}`
						: "ファイルの削除に失敗しました",
				);
			}
		} catch (err: unknown) {
			await handleAuthError(err as { message: string });
		} finally {
			setLoading(false);
		}
	}, [files, fetchFiles, user, clearError, handleAuthError, authFetch]);

	const handleSelect = useCallback((fileName: string, checked: boolean) => {
		setFiles((prevFiles) =>
			prevFiles.map((file) =>
				file.file_name === fileName ? { ...file, select: checked } : file,
			),
		);
	}, []);

	const createAiContent = useCallback(
		async (
			type: "ai-output" | "ai-exercise/stream" | "ai-exercise/multiple-choice",
		) => {
			if (!user) {
				setError("認証が必要です");
				return;
			}

			const selectedFiles = files
				.filter((file) => file.select)
				.map((file) => file.file_name);
			if (!title || selectedFiles.length === 0) {
				setError("ファイルを選択してタイトルを入力してください");
				return;
			}

			try {
				// キャッシュクリアの処理
				if (type === "ai-exercise/multiple-choice") {
					for (const key of Object.values(CACHE_KEYS.MULTI_CHOICE)) {
						localStorage.removeItem(key);
					}
				} else if (type === "ai-exercise/stream") {
					for (const key of Object.values(CACHE_KEYS.STREAM_EXERCISE)) {
						localStorage.removeItem(key);
					}
				}

				// 選択されたファイルとタイトルを保存
				localStorage.setItem("selectedFiles", JSON.stringify(selectedFiles));
				localStorage.setItem("title", title);
				localStorage.setItem("uid", user.uid);
				router.push(`/${type}`);
			} catch (err) {
				setError("データの保存に失敗しました。もう一度お試しください。");
			}
		},
		[files, title, router, user],
	);

	const resetAll = useCallback(() => {
		setFiles((prevFiles) =>
			prevFiles.map((file) => ({ ...file, select: false })),
		);
		setTitle("");
	}, []);

	const handleSelectAll = useCallback((checked: boolean) => {
		setFiles((prevFiles) =>
			prevFiles.map((file) => ({
				...file,
				select: checked,
			})),
		);
	}, []);

	const selectedFileNames = useMemo(
		() =>
			files
				.filter((f) => f.select)
				.map((f) => f.file_name)
				.join(", "),
		[files],
	);

	const isAnyFileSelected = useMemo(
		() => files.some((file) => file.select),
		[files],
	);

	const areAllFilesSelected = useMemo(
		() => files.length > 0 && files.every((file) => file.select),
		[files],
	);

	useEffect(() => {
		if (user) {
			fetchFiles();
		} else {
			setFiles([]);
		}
	}, [user, fetchFiles]);

	useEffect(() => {
		if (authError) {
			setError(authError);
		}
	}, [authError]);

	if (!user) {
		return (
			<div className="container mx-auto p-4">
				<Alert variant="gradient">
					このページにアクセスするにはログインが必要です
				</Alert>
			</div>
		);
	}

	return (
		<div className="container mx-auto p-4">
			<Card className="w-full">
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						AI ノート/練習問題
					</Typography>
				</CardHeader>

				<CardBody className="flex flex-col gap-4">
					<div className="flex gap-4">
						<Button
							onClick={fetchFiles}
							disabled={loading}
							className="flex items-center gap-2"
						>
							{loading && <Spinner className="h-4 w-4" />}
							ファイル更新
						</Button>
						<Button variant="outlined" onClick={resetAll} disabled={loading}>
							リセット
						</Button>
						<Button
							onClick={deleteSelectedFiles}
							disabled={!isAnyFileSelected || loading}
						>
							選択項目を削除
						</Button>
					</div>

					{error && (
						<Alert
							variant="gradient"
							onClose={() => {
								setError("");
								clearError();
							}}
						>
							{error}
						</Alert>
					)}

					{success && (
						<Alert variant="gradient" onClose={() => setSuccess("")}>
							{success}
						</Alert>
					)}

					{loading && (
						<div className="flex justify-center p-4">
							<Spinner className="h-8 w-8" />
						</div>
					)}

					{!loading && files.length > 0 && (
						<FileTable
							files={files}
							loading={loading}
							handleSelect={handleSelect}
							handleSelectAll={handleSelectAll}
							areAllFilesSelected={areAllFilesSelected}
							formatDate={formatDate}
						/>
					)}

					{!loading && files.length === 0 && (
						<Alert variant="gradient">ファイルが見つかりません</Alert>
					)}

					{isAnyFileSelected && (
						<div className="space-y-4">
							<div>
								<Typography variant="h6">選択されたファイル</Typography>
								<Typography variant="small" className="text-gray-600">
									{selectedFileNames}
								</Typography>
							</div>

							<div>
								<Typography variant="h6">タイトル</Typography>
								<Input
									value={title}
									onChange={(e) => setTitle(e.target.value)}
									placeholder="AIノート/演習のタイトルを入力してください（最大100文字）"
									maxLength={100}
									className="mt-1 focus:outline-none !border !border-gray-300 focus:!border-gray-900 rounded-lg"
									labelProps={{
										className: "before:content-none after:content-none",
									}}
									disabled={loading}
								/>
							</div>

							{title && (
								<div className="flex gap-4">
									<Button
										size="lg"
										onClick={() => createAiContent("ai-output")}
										className="flex-1"
										disabled={loading}
									>
										AIノート作成
									</Button>
									<Button
										size="lg"
										onClick={() => createAiContent("ai-exercise/stream")}
										className="flex-1"
										disabled={loading}
									>
										AI練習問題
									</Button>
									<Button
										size="lg"
										onClick={() =>
											createAiContent("ai-exercise/multiple-choice")
										}
										className="flex-1"
										disabled={loading}
									>
										選択問題テスト
									</Button>
								</div>
							)}
						</div>
					)}
				</CardBody>
			</Card>
		</div>
	);
}
