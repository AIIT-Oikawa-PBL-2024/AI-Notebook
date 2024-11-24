import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { useCallback, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_DELETE_FILES = `${BACKEND_HOST}/files/delete_files`;

interface FileData {
	file_name: string;
	file_size: string;
	created_at: string;
	select?: boolean;
	id?: string;
	user_id?: string;
}

interface UseFileDeleteReturn {
	loading: boolean;
	error: string;
	success: string;
	deleteSelectedFiles: (files: FileData[]) => Promise<void>;
	clearSuccess: () => void;
	clearError: () => void;
}

export const useFileDelete = (
	onDeleteSuccess?: () => Promise<void>,
): UseFileDeleteReturn => {
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState("");
	const [success, setSuccess] = useState("");
	const authFetch = useAuthFetch();
	const { user, clearError: clearAuthError, reAuthenticate } = useAuth();

	const handleAuthError = useCallback(
		async (error: { message: string }) => {
			if (error.message.includes("token") || error.message.includes("認証")) {
				await reAuthenticate();
			}
			setError(error.message);
		},
		[reAuthenticate],
	);

	const deleteSelectedFiles = useCallback(
		async (files: FileData[]) => {
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
					clearAuthError();
					if (onDeleteSuccess) {
						await onDeleteSuccess();
					}
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
		},
		[user, clearAuthError, handleAuthError, authFetch, onDeleteSuccess],
	);

	const clearSuccess = useCallback(() => {
		setSuccess("");
	}, []);

	const clearError = useCallback(() => {
		setError("");
	}, []);

	return {
		loading,
		error,
		success,
		deleteSelectedFiles,
		clearSuccess,
		clearError,
	};
};
