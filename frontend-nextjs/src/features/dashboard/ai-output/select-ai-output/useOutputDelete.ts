import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_OUTPUTS = `${BACKEND_HOST}/outputs`;

interface UseOutputDeleteProps {
	onSuccess?: () => void;
	onError?: (error: string) => void;
}

interface UseOutputDeleteReturn {
	deleteOutput: (outputId: number) => Promise<void>;
	isDeleting: boolean;
	error: string | null;
}

export const useOutputDelete = ({
	onSuccess,
	onError,
}: UseOutputDeleteProps = {}): UseOutputDeleteReturn => {
	const [isDeleting, setIsDeleting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const authFetch = useAuthFetch();
	const router = useRouter();

	const deleteOutput = useCallback(
		async (outputId: number) => {
			if (!outputId) {
				const errorMessage = "削除するAI出力が選択されていません。";
				setError(errorMessage);
				onError?.(errorMessage);
				return;
			}

			setIsDeleting(true);
			setError(null);

			try {
				const response = await authFetch(
					`${BACKEND_API_URL_OUTPUTS}/${outputId}`,
					{
						method: "DELETE",
						headers: {
							"Content-Type": "application/json",
						},
					},
				);

				if (!response.ok) {
					throw new Error("AI出力の削除に失敗しました。");
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
		deleteOutput,
		isDeleting,
		error,
	};
};
