import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useEffect, useState } from "react";

export function useExerciseGenerator() {
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [exercise, setExercise] = useState("");
	const authFetch = useAuthFetch();

	useEffect(() => {
		const generateExercise = async () => {
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
					`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/request_stream`,
					{
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify(selectedFiles),
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
				}
			} catch (err) {
				setError((err as Error).message);
			} finally {
				setLoading(false);
			}
		};

		generateExercise();
	}, [authFetch]);

	return { loading, error, exercise };
}
