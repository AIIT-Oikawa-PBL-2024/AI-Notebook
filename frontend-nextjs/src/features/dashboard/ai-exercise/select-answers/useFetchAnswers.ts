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

export const useFetchAnswers = () => {
	const [answers, setAnswers] = useState<AnswerResponse[]>([]);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string>("");
	const authFetch = useAuthFetch();

	const fetchAnswers = useCallback(async () => {
		setLoading(true);
		setError("");

		try {
			const response = await authFetch(BACKEND_API_URL_GET_ANSWERS);

			if (!response.ok) {
				throw new Error("回答データの取得に失敗しました");
			}

			const data: AnswerResponse[] = await response.json();
			setAnswers(data);
		} catch (err) {
			setError(
				err instanceof Error ? err.message : "不明なエラーが発生しました",
			);
		} finally {
			setLoading(false);
		}
	}, [authFetch]);

	useEffect(() => {
		fetchAnswers();
	}, [fetchAnswers]);

	return { answers, loading, error, refetch: fetchAnswers };
};
