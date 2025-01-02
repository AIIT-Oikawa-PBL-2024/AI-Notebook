import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useState } from "react";

// 選択肢の型定義
export interface Choice {
	choice_a: string;
	choice_b: string;
	choice_c: string;
	choice_d: string;
}

// 問題の型定義
export interface Question {
	question_id: string;
	question_text: string;
	choices: Choice;
	answer: string;
	explanation: string;
}

// APIレスポンスの型定義
export interface ExerciseResponse {
	id: string;
	content: [
		{
			id: string;
			input: {
				questions: Question[];
			};
			name: string;
			type: string;
		},
	];
}

// ユーザーの解答データの型定義
export interface AnswerResponseData {
	question_id: string;
	question_text: string;
	choices: Choice;
	user_selected_choice: string;
	correct_choice: string;
	is_correct: boolean;
	explanation: string;
}

// バックエンドに送信するペイロードの型定義
export interface SaveAnswerPayload {
	title: string;
	relatedFiles: string[];
	responses: AnswerResponseData[];
}

// フックの戻り値の型定義
interface SimilarQuestionsResult {
	similarQuestions: (payload: SaveAnswerPayload) => Promise<void>;
	loading: boolean;
	error: string | null;
	success: boolean;
	exercise: ExerciseResponse | null;
}

// ローカルストレージのキー
const SIMILAR_QUESTIONS_STORAGE_KEY = "cached_similar_questions";
const SIMILAR_QUESTIONS_STATUS_KEY = "similar_questions_generation_status";

export function useMakeSimilarQuestions(): SimilarQuestionsResult {
	// 状態管理
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [success, setSuccess] = useState(false);

	// 生成された類似問題のキャッシュを初期化
	const [exercise, setExercise] = useState<ExerciseResponse | null>(() => {
		if (typeof window !== "undefined") {
			const cached = localStorage.getItem(SIMILAR_QUESTIONS_STORAGE_KEY);
			return cached ? JSON.parse(cached) : null;
		}
		return null;
	});

	const authFetch = useAuthFetch();

	// 類似問題を生成する関数
	const similarQuestions = async (payload: SaveAnswerPayload) => {
		setLoading(true);
		setError(null);
		setSuccess(false);

		try {
			// バックエンドAPIにリクエスト
			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/similar_multiple_choice_question`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(payload),
				},
			);

			// エラーハンドリング
			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "類似問題の生成に失敗しました。");
			}

			// レスポンスの処理
			const data: ExerciseResponse = await response.json();
			setExercise(data);

			// キャッシュの保存
			localStorage.setItem(SIMILAR_QUESTIONS_STORAGE_KEY, JSON.stringify(data));
			localStorage.setItem(SIMILAR_QUESTIONS_STATUS_KEY, "completed");
			setSuccess(true);
		} catch (err) {
			setError((err as Error).message);
		} finally {
			setLoading(false);
		}
	};

	// フックの戻り値
	return { similarQuestions, loading, error, success, exercise };
}
