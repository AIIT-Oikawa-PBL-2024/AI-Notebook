import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useEffect, useRef, useState } from "react";

interface File {
	id: string;
	file_name: string;
	file_size: string;
	created_at: string;
	user_id: string;
}

interface Question {
	question_id: string;
	question_text: string;
	answer: string;
	explanation: string;
}

interface ParsedResponse {
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

interface Exercise {
	id: number;
	title: string;
	response: string;
	exercise_type: string;
	user_id: string;
	created_at: string;
	files: File[];
}

const STORAGE_KEY = "cached_essay_question";
const GENERATION_STATUS_KEY = "essay_generation_status";

export function useGetEssayQuestion(id?: string) {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [exercise, setExercise] = useState<Exercise | null>(() => {
		if (typeof window !== "undefined") {
			const cached = localStorage.getItem(STORAGE_KEY);
			return cached ? JSON.parse(cached) : null;
		}
		return null;
	});

	const [parsedResponse, setParsedResponse] = useState<ParsedResponse | null>(
		null,
	);
	const isGenerating = useRef(false);
	const hasInitialized = useRef(false);

	const authFetch = useAuthFetch();

	const parseExerciseResponse = useCallback((exercise: Exercise) => {
		try {
			const parsed = JSON.parse(exercise.response);
			setParsedResponse(parsed);
		} catch (err) {
			console.error("Failed to parse exercise response:", err);
			setError("問題データの解析に失敗しました");
		}
	}, []);

	const generateExercise = useCallback(async () => {
		// 初期化済み、かつ生成中の場合は早期リターン
		if (hasInitialized.current || isGenerating.current) return;

		// id がない場合のストレージチェック
		if (!id) {
			const generationStatus = localStorage.getItem(GENERATION_STATUS_KEY);
			const cached = localStorage.getItem(STORAGE_KEY);

			if (generationStatus === "completed" && cached) {
				try {
					const cachedExercise = JSON.parse(cached);
					setExercise(cachedExercise);
					parseExerciseResponse(cachedExercise);
					setLoading(false);
					hasInitialized.current = true;
					return;
				} catch (err) {
					console.error("Failed to parse cached exercise:", err);
				}
			}
		}

		isGenerating.current = true;

		try {
			const selectedFiles = JSON.parse(
				localStorage.getItem("selectedFiles") || "[]",
			);
			const title = localStorage.getItem("title");

			if (!id && (!selectedFiles || !title)) {
				throw new Error("必要な情報が見つかりません");
			}

			const endpoint = id
				? `${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/${id}`
				: `${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/essay_question`;

			const options = id
				? {
						method: "GET",
					}
				: {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({
							files: selectedFiles,
							title: title,
						}),
					};

			const response = await authFetch(endpoint, options);

			if (!response.ok) {
				throw new Error("記述問題の取得に失敗しました");
			}

			const data: Exercise = await response.json();
			setExercise(data);
			parseExerciseResponse(data);

			if (!id) {
				localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
				localStorage.setItem(GENERATION_STATUS_KEY, "completed");
			}
		} catch (err) {
			setError((err as Error).message);
		} finally {
			setLoading(false);
			isGenerating.current = false;
			hasInitialized.current = true;
		}
	}, [authFetch, id, parseExerciseResponse]);

	useEffect(() => {
		generateExercise();
	}, [generateExercise]);

	const resetExercise = useCallback(() => {
		hasInitialized.current = false; // 初期化フラグをリセット
		if (!id) {
			localStorage.removeItem(STORAGE_KEY);
			localStorage.removeItem(GENERATION_STATUS_KEY);
		}
		setExercise(null);
		setParsedResponse(null);
		setError("");
		setLoading(true);
		isGenerating.current = false;
		generateExercise(); // 問題を再生成
	}, [id, generateExercise]);

	const clearCache = useCallback(() => {
		hasInitialized.current = false; // 初期化フラグをリセット
		if (!id) {
			localStorage.removeItem(STORAGE_KEY);
			localStorage.removeItem(GENERATION_STATUS_KEY);
		}
		setExercise(null);
		setParsedResponse(null);
		setError("");
		setLoading(true);
		isGenerating.current = false;
		generateExercise(); // 問題を再生成
	}, [id, generateExercise]);

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
		parsedResponse,
		resetExercise,
		clearCache,
		checkCache,
	};
}
