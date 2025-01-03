// frontend-nextjs/src/features/dashboard/ai-exercise/select-answers/useFetchAnswers.ts

import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useEffect, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_ANSWERS = `${BACKEND_HOST}/answers/list`;

export interface AnswerResponse {
	id: number;
	title: string;
	related_files: string[];
	question_id: string;
	question_text: string;
	choice_a: string;
	choice_b: string;
	choice_c: string;
	choice_d: string;
	user_selected_choice: string;
	correct_choice: string;
	is_correct: boolean;
	explanation: string;
	user_id: string;
	created_at: string; // ISO形式の文字列
	updated_at: string; // ISO形式の文字列
}

interface PaginatedResponse {
	total: number;
	answers: AnswerResponse[];
}

export const useFetchAnswers = () => {
	const [answers, setAnswers] = useState<AnswerResponse[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string>("");

	// ページネーション用に追加した state
	const [totalCount, setTotalCount] = useState<number>(0);
	const [currentPage, setCurrentPage] = useState<number>(1);
	const [totalPages, setTotalPages] = useState<number>(0);

	const authFetch = useAuthFetch();

	// ページネーションに対応するよう引数 (page, limit) を追加
	const fetchAnswers = useCallback(
		async (page = 1, limit = 10) => {
			setLoading(true);
			setError("");

			try {
				// ページネーション用に skip を計算
				const skip = (page - 1) * limit;

				const response = await authFetch(
					`${BACKEND_API_URL_GET_ANSWERS}?skip=${skip}&limit=${limit}`,
				);

				if (!response.ok) {
					throw new Error("回答データの取得に失敗しました");
				}

				const data: PaginatedResponse = await response.json();

				// ページネーションされたオブジェクトとして扱う
				setAnswers(data.answers);
				setTotalCount(data.total);
				setCurrentPage(page);
				setTotalPages(Math.ceil(data.total / limit));
			} catch (err) {
				setError(
					err instanceof Error ? err.message : "不明なエラーが発生しました",
				);
			} finally {
				setLoading(false);
			}
		},
		[authFetch],
	);

	useEffect(() => {
		// 初回マウント時に1ページ目を取得
		fetchAnswers(1, 10);
	}, [fetchAnswers]);

	// 既存の戻り値を保持しつつ、ページネーション用の state を追加して返却
	return {
		answers,
		loading,
		error,
		refetch: fetchAnswers,
		// ▼ ページネーション用に追加
		totalCount,
		currentPage,
		totalPages,
	};
};
