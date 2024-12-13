import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_NOTES = `${BACKEND_HOST}/notes`;

interface UseNoteDeleteProps {
	onSuccess?: () => void;
	onError?: (error: string) => void;
}

interface UseNoteDeleteReturn {
	deleteNote: (noteId: number) => Promise<void>;
	isDeleting: boolean;
	error: string | null;
}

export const useNoteDelete = ({
	onSuccess,
	onError,
}: UseNoteDeleteProps = {}): UseNoteDeleteReturn => {
	const [isDeleting, setIsDeleting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const authFetch = useAuthFetch();
	const router = useRouter();

	const deleteNote = useCallback(
		async (noteId: number) => {
			if (!noteId) {
				const errorMessage = "削除するノートが選択されていません。";
				setError(errorMessage);
				onError?.(errorMessage);
				return;
			}

			setIsDeleting(true);
			setError(null);

			try {
				const response = await authFetch(`${BACKEND_API_URL_NOTES}/${noteId}`, {
					method: "DELETE",
					headers: {
						"Content-Type": "application/json",
					},
				});

				if (!response.ok) {
					// バックエンドから返されるエラーメッセージを処理
					const data = await response.json();
					if (response.status === 404) {
						throw new Error(data.detail || "ノートが見つかりません。");
					}
					throw new Error(data.detail || "ノートの削除に失敗しました。");
				}

				// 削除成功時の処理
				onSuccess?.();
				router.refresh(); // App Router のキャッシュを更新
			} catch (err) {
				const errorMessage =
					err instanceof Error ? err.message : "予期せぬエラーが発生しました。";
				setError(errorMessage);
				onError?.(errorMessage);
			} finally {
				setIsDeleting(false);
			}
		},
		[authFetch, router, onSuccess, onError],
	);

	return {
		deleteNote,
		isDeleting,
		error,
	};
};
