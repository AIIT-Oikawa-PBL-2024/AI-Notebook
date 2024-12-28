import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useState } from "react";

export interface Choice {
	choice_a: string;
	choice_b: string;
	choice_c: string;
	choice_d: string;
}

export interface Question {
	question_id: string;
	question_text: string;
	choices: Choice;
	answer: string;
	explanation: string;
}

export interface AnswerResponseData {
	question_id: string;
	question_text: string;
	choices: Choice;
	user_selected_choice: string;
	correct_choice: string;
	is_correct: boolean;
	explanation: string; // 追加されたフィールド
}

export interface SaveAnswerPayload {
	title: string;
	relatedFiles: string[];
	responses: AnswerResponseData[];
}

interface SaveAnswersResult {
	saveAnswers: (payload: SaveAnswerPayload) => Promise<void>;
	loading: boolean;
	error: string | null;
	success: boolean;
}

// ユーザーの回答データを直接バックエンドに送信して保存
export function useSaveAnswers(): SaveAnswersResult {
	const [loading, setLoading] = useState(false); // ローディング状態
	const [error, setError] = useState<string | null>(null); // エラーメッセージ
	const [success, setSuccess] = useState(false); // 保存成功状態

	const authFetch = useAuthFetch();

	// ユーザーの回答データをバックエンドに送信して保存
	const saveAnswers = async (payload: SaveAnswerPayload) => {
		setLoading(true);
		setError(null);
		setSuccess(false);

		try {
			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/answers/save_answers`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(payload),
				},
			);

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.message || "選択問題の保存に失敗しました。");
			}

			setSuccess(true); // 保存成功を設定
		} catch (err) {
			setError((err as Error).message); // エラーメッセージを設定
		} finally {
			setLoading(false); // ローディングを終了
		}
	};

	return { saveAnswers, loading, error, success };
}
