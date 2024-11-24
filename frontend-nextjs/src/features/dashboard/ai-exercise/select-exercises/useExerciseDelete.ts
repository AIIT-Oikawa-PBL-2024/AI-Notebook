import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_EXERCISES = `${BACKEND_HOST}/exercises`;

interface UseExerciseDeleteProps {
	onSuccess?: () => void;
	onError?: (error: string) => void;
}

interface UseExerciseDeleteReturn {
	deleteExercise: (exerciseId: number) => Promise<void>;
	isDeleting: boolean;
	error: string | null;
}

export const useExerciseDelete = ({
	onSuccess,
	onError,
}: UseExerciseDeleteProps = {}): UseExerciseDeleteReturn => {
	const [isDeleting, setIsDeleting] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const authFetch = useAuthFetch();
	const router = useRouter();

	const deleteExercise = useCallback(
		async (exerciseId: number) => {
			if (!exerciseId) {
				const errorMessage = "削除する問題が選択されていません。";
				setError(errorMessage);
				onError?.(errorMessage);
				return;
			}

			setIsDeleting(true);
			setError(null);

			try {
				const response = await authFetch(
					`${BACKEND_API_URL_EXERCISES}/${exerciseId}`,
					{
						method: "DELETE",
						headers: {
							"Content-Type": "application/json",
						},
					},
				);

				if (!response.ok) {
					throw new Error("問題の削除に失敗しました。");
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
		deleteExercise,
		isDeleting,
		error,
	};
};
