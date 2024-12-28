import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_BULK_DELETE = `${BACKEND_HOST}/answers/bulk_delete`;

// API レスポンスの型定義
export interface DeleteAnswersResult {
	deleted_ids: number[];
	not_found_ids: number[];
	unauthorized_ids: number[];
}

// 指定した回答IDリストの一括削除を行うカスタムフック
export const useDeleteAnswers = () => {
	const authFetch = useAuthFetch(); // 認証情報付き fetch
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string>("");

	// 指定した回答IDリストの一括削除を行う
	const deleteAnswers = async (
		answerIds: number[],
	): Promise<DeleteAnswersResult> => {
		try {
			// ローディング状態を同期的に設定
			setLoading(true);
			setError("");

			const response = await authFetch(BACKEND_API_URL_BULK_DELETE, {
				method: "DELETE",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ answer_ids: answerIds }),
			});

			if (!response.ok) {
				throw new Error("回答の一括削除に失敗しました。");
			}

			const data: DeleteAnswersResult = await response.json();
			return data;
		} catch (err) {
			const message =
				err instanceof Error ? err.message : "不明なエラーが発生しました。";
			setError(message);
			throw err;
		} finally {
			// 最後に必ずローディング状態を解除
			setLoading(false);
		}
	};

	return { deleteAnswers, loading, error };
};
