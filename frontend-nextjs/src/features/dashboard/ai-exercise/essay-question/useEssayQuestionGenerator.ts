import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useEffect, useRef, useState } from "react";

// レスポンスの型定義

interface Question {
	question_id: string;
	question_text: string;
	answer: string;
	explanation: string;
}

interface ExerciseResponse {
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
	exercise_id: number;
}

const STORAGE_KEY = "cached_essay_question";
const GENERATION_STATUS_KEY = "essay_generation_status";

export function useEssayQuestionGenerator() {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [exercise, setExercise] = useState<ExerciseResponse | null>(() => {
		if (typeof window !== "undefined") {
			const cached = localStorage.getItem(STORAGE_KEY);
			return cached ? JSON.parse(cached) : null;
		}
		return null;
	});

	const authFetch = useAuthFetch();
	const isGenerating = useRef(false);

	const generateExercise = useCallback(async () => {
		// すでに生成が完了している場合は再生成しない
		const generationStatus = localStorage.getItem(GENERATION_STATUS_KEY);
		if (generationStatus === "completed" && exercise) {
			setLoading(false);
			return;
		}

		// 生成が実行中の場合は早期リターン
		if (isGenerating.current) {
			return;
		}

		isGenerating.current = true;

		try {
			const selectedFiles = JSON.parse(
				localStorage.getItem("selectedFiles") || "[]",
			);
			const title = localStorage.getItem("title");

			if (!selectedFiles || !title) {
				throw new Error("必要な情報が見つかりません");
			}

			setLoading(true);
			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/essay_question`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						files: selectedFiles,
						title: title,
					}),
				},
			);

			if (!response.ok) {
				throw new Error("記述問題の生成に失敗しました");
			}

			const data: ExerciseResponse = await response.json();
			setExercise(data);
			localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
			localStorage.setItem(GENERATION_STATUS_KEY, "completed");
		} catch (err) {
			setError((err as Error).message);
		} finally {
			setLoading(false);
			isGenerating.current = false;
		}
	}, [authFetch, exercise]);

	useEffect(() => {
		generateExercise();
	}, [generateExercise]);

	// 問題のリセット（再生成のトリガー）
	const resetExercise = useCallback(() => {
		localStorage.removeItem(STORAGE_KEY);
		localStorage.removeItem(GENERATION_STATUS_KEY);
		setExercise(null);
		setError("");
		setLoading(true);
		isGenerating.current = false;
	}, []);

	// 記述問題のストレージをクリア（完全な初期状態に）
	const clearCache = useCallback(() => {
		// 記述問題関連のストレージのみ削除
		localStorage.removeItem(STORAGE_KEY);
		localStorage.removeItem(GENERATION_STATUS_KEY);
		// 状態のリセット
		setExercise(null);
		setError("");
		setLoading(true);
		isGenerating.current = false;
	}, []);

	// ストレージの確認
	const checkCache = useCallback(() => {
		const cache = {
			exercise: localStorage.getItem(STORAGE_KEY),
			generationStatus: localStorage.getItem(GENERATION_STATUS_KEY),
		};
		return cache;
	}, []);

	return {
		loading,
		error,
		exercise,
		resetExercise, // 問題のリセット（再生成のトリガー）
		clearCache, // 記述問題のストレージのみクリア
		checkCache, // ストレージ確認
	};
}
