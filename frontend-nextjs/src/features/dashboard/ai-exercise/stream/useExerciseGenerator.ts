"use client";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "cached_exercise";
const GENERATION_STATUS_KEY = "exercise_generation_status";

export function useExerciseGenerator() {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [exercise, setExercise] = useState(() => {
		if (typeof window !== "undefined") {
			return localStorage.getItem(STORAGE_KEY) || "";
		}
		return "";
	});
	const [title, setTitle] = useState(() => {
		if (typeof window !== "undefined") {
			return localStorage.getItem("title") || "";
		}
		return "";
	});
	const authFetch = useAuthFetch();
	const isGenerating = useRef(false);

	// generateExercise 関数を useCallback でメモ化
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
			const storedTitle = localStorage.getItem("title");
			const difficulty = localStorage.getItem("difficulty");

			if (!selectedFiles || !storedTitle || !difficulty) {
				throw new Error("必要な情報が見つかりません");
			}

			setTitle(storedTitle); // タイトルの状態を更新
			setLoading(true);

			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/request_stream`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({
						files: selectedFiles,
						title: title,
						difficulty: difficulty,
					}),
				},
			);

			if (!response.ok) {
				throw new Error("AI練習問題の生成に失敗しました");
			}

			const reader = response.body?.getReader();
			if (!reader) {
				throw new Error("ストリーミングの初期化に失敗しました");
			}

			let accumulatedContent = "";
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;

				const chunk = new TextDecoder().decode(value);
				accumulatedContent += chunk;
				setExercise(accumulatedContent);
				localStorage.setItem(STORAGE_KEY, accumulatedContent);
			}

			localStorage.setItem(GENERATION_STATUS_KEY, "completed");
		} catch (err) {
			setError((err as Error).message);
		} finally {
			setLoading(false);
			isGenerating.current = false;
		}
	}, [authFetch, exercise, title]); // exercise と title を依存配列に含める（ステータスチェックに使用）

	useEffect(() => {
		generateExercise();
	}, [generateExercise]); // generateExercise のみを依存配列に含める

	const resetExercise = useCallback(() => {
		localStorage.removeItem(STORAGE_KEY);
		localStorage.removeItem(GENERATION_STATUS_KEY);
		setExercise("");
		setError("");
		setLoading(true);
		isGenerating.current = false;
	}, []);

	return { loading, error, exercise, title, resetExercise };
}
