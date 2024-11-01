"use client";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import type { FileData } from "@/types/files";
import {
	Alert,
	Button,
	Card,
	CardBody,
	CardHeader,
	Checkbox,
	Input,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_FILES = `${BACKEND_HOST}/files/`;
const BACKEND_API_URL_DELETE_FILES = `${BACKEND_HOST}/files/delete_files`;

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
		async (type: "note" | "exercise") => {
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
				// AI練習問題の場合は、既存のキャッシュをクリア
				if (type === "exercise") {
					localStorage.removeItem("cached_exercise");
					localStorage.removeItem("exercise_generation_status");
				}

				// 選択されたファイルとタイトルを保存
				localStorage.setItem("selectedFiles", JSON.stringify(selectedFiles));
				localStorage.setItem("title", title);
				localStorage.setItem("uid", user.uid);
				router.push(`/ai-content/${type}`);
			} catch (err) {
				setError("データの保存に失敗しました。もう一度お試しください。");
			}
		},
		[files, title, router, user],
	);

	const resetAll = useCallback(() => {
		setFiles([]);
		setTitle("");
		setError("");
		setSuccess("");
		clearError();
	}, [clearError]);

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
		const mounted = { current: true };

		if (user) {
			fetchFiles();
		} else {
			setFiles([]);
		}

		return () => {
			mounted.current = false;
		};
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
						<Card>
							<table className="w-full min-w-max table-auto text-left">
								<thead>
									<tr>
										<th className="border-b p-4">
											<Checkbox
												checked={areAllFilesSelected}
												onChange={(e) => handleSelectAll(e.target.checked)}
												disabled={loading}
											/>
										</th>
										<th className="border-b p-4">
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												ファイル名
											</Typography>
										</th>
										<th className="border-b p-4">
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												サイズ
											</Typography>
										</th>
										<th className="border-b p-4">
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												作成日時
											</Typography>
										</th>
									</tr>
								</thead>
								<tbody>
									{files.map((file) => (
										<tr key={file.file_name}>
											<td className="p-4">
												<Checkbox
													checked={file.select}
													onChange={(e) =>
														handleSelect(file.file_name, e.target.checked)
													}
													disabled={loading}
												/>
											</td>
											<td className="p-4">
												<Typography variant="small">
													{file.file_name}
												</Typography>
											</td>
											<td className="p-4">
												<Typography variant="small">
													{file.file_size}
												</Typography>
											</td>
											<td className="p-4">
												<Typography variant="small">
													{formatDate(file.created_at)}
												</Typography>
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</Card>
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
									className="mt-1"
									disabled={loading}
								/>
							</div>

							{title && (
								<div className="flex gap-4">
									<Button
										size="lg"
										onClick={() => createAiContent("note")}
										className="flex-1"
										disabled={loading}
									>
										AIノート作成
									</Button>
									<Button
										size="lg"
										onClick={() => createAiContent("exercise")}
										className="flex-1"
										disabled={loading}
									>
										AI練習問題
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
