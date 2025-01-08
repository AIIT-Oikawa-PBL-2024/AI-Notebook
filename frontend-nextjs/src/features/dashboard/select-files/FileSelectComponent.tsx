"use client";

import { PopupDialog } from "@/components/elements/PopupDialog";
import FileTable from "@/features/dashboard/select-files/FileTableComponent";
import { useFileDelete } from "@/features/dashboard/select-files/useFileDelete";
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

interface FileData {
	file_name: string;
	file_size: string;
	created_at: string;
	select?: boolean;
	id?: string;
	user_id?: string;
}

// 選択問題関連のストレージキーを定数として定義
const STORAGE_KEYS = {
	MULTI_CHOICE: {
		QUESTION: "cached_multi_choice_question",
		GENERATION_STATUS: "multi_choice_generation_status",
		ANSWERS: "cached_answers",
		RESULTS: "cached_results_state",
	},
	ESSAY_QUESTION: {
		QUESTION: "cached_essay_question",
		GENERATION_STATUS: "essay_question_generation_status",
		ANSWERS: "cached_essay_answers",
		RESULTS: "cached_essay_results_state",
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

	const {
		loading: deleteLoading,
		error: deleteError,
		success: deleteSuccess,
		deleteSelectedFiles,
		clearSuccess,
		clearError: clearDeleteError,
	} = useFileDelete(fetchFiles);

	const handleDeleteSelectedFiles = useCallback(async () => {
		await deleteSelectedFiles(files);
	}, [deleteSelectedFiles, files]);

	const handleSelect = useCallback((fileName: string, checked: boolean) => {
		setFiles((prevFiles) =>
			prevFiles.map((file) =>
				file.file_name === fileName ? { ...file, select: checked } : file,
			),
		);
	}, []);

	const createAiContent = useCallback(
		async (
			type:
				| "ai-output/stream"
				| "ai-exercise/stream"
				| "ai-exercise/multiple-choice"
				| "ai-exercise/essay-question",
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
				// ストレージクリアの処理
				if (type === "ai-exercise/multiple-choice") {
					for (const key of Object.values(STORAGE_KEYS.MULTI_CHOICE)) {
						localStorage.removeItem(key);
					}
				} else if (type === "ai-exercise/stream") {
					for (const key of Object.values(STORAGE_KEYS.STREAM_EXERCISE)) {
						localStorage.removeItem(key);
					}
				} else if (type === "ai-exercise/essay-question") {
					for (const key of Object.values(STORAGE_KEYS.ESSAY_QUESTION)) {
						localStorage.removeItem(key);
					}
				} else if (type === "ai-output/stream") {
					localStorage.removeItem("cached_output");
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
						ファイル選択
					</Typography>
				</CardHeader>

				<CardBody className="flex flex-col gap-4">
					<div className="flex gap-4">
						<Button
							onClick={fetchFiles}
							disabled={loading || deleteLoading}
							className="flex items-center gap-2"
						>
							{(loading || deleteLoading) && <Spinner className="h-4 w-4" />}
							ファイル更新
						</Button>
						<Button
							variant="outlined"
							onClick={resetAll}
							disabled={loading || deleteLoading}
						>
							リセット
						</Button>
						<PopupDialog
							buttonTitle="選択項目を削除"
							title="選択項目を削除しますか？"
							actionProps={{ onClick: handleDeleteSelectedFiles }}
							triggerButtonProps={{
								disabled: !isAnyFileSelected || loading || deleteLoading,
							}}
						/>
					</div>

					{(error || deleteError) && (
						<Alert
							variant="gradient"
							onClose={() => {
								setError("");
								clearDeleteError();
								clearError();
							}}
						>
							{error || deleteError}
						</Alert>
					)}

					{success && (
						<Alert variant="gradient" onClose={() => setSuccess("")}>
							{success}
						</Alert>
					)}

					{deleteSuccess && (
						<Alert variant="gradient" onClose={clearSuccess}>
							{deleteSuccess}
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
								placeholder="AI要約/練習問題のタイトルを入力してください（最大100文字）"
								maxLength={100}
								className="mt-1 focus:outline-none !border !border-gray-300 focus:!border-gray-900 rounded-lg"
								labelProps={{
									className: "before:content-none after:content-none",
								}}
								disabled={loading}
							/>
						</div>

						<div className="flex gap-4">
							<Button
								size="lg"
								onClick={() => createAiContent("ai-output/stream")}
								className="flex-1"
								disabled={loading || !isAnyFileSelected || !title}
							>
								AI要約作成
							</Button>
							<Button
								size="lg"
								onClick={() => createAiContent("ai-exercise/stream")}
								className="flex-1"
								disabled={loading || !isAnyFileSelected || !title}
							>
								AI練習問題
							</Button>
							<Button
								size="lg"
								onClick={() => createAiContent("ai-exercise/multiple-choice")}
								className="flex-1"
								disabled={loading || !isAnyFileSelected || !title}
							>
								選択問題テスト
							</Button>
							<Button
								size="lg"
								onClick={() => createAiContent("ai-exercise/essay-question")}
								className="flex-1"
								disabled={loading || !isAnyFileSelected || !title}
							>
								記述問題テスト
							</Button>
						</div>
					</div>
				</CardBody>
			</Card>
		</div>
	);
}
