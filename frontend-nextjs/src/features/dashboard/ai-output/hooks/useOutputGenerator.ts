import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useEffect, useRef, useState } from "react";

const STORAGE_KEY = "cached_output";
const GENERATION_STATUS_KEY = "output_generation_status";

export function useOutputGenerator() {
	const fileNames = ["3_規範的なプロセスモデル.pdf"];
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [output, setOutput] = useState(() => {
		if (typeof window !== "undefined") {
			return localStorage.getItem(STORAGE_KEY) || "";
		}
		return "";
	});
	const authFetch = useAuthFetch();
	const isGenerating = useRef(false);

	// generateOutput 関数を useCallback でメモ化
	const generateOutput = useCallback(async () => {
		// すでに生成が完了している場合は再生成しない
		const generationStatus = localStorage.getItem(GENERATION_STATUS_KEY);
		if (generationStatus === "completed" && output) {
			setLoading(false);
			return;
		}

		// 生成が実行中の場合は早期リターン
		if (isGenerating.current) {
			return;
		}

		isGenerating.current = true;

		try {
			setLoading(true);
			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/outputs/request_stream`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(fileNames),
				},
			);

			if (!response.ok) {
				throw new Error("AIノートの生成に失敗しました");
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
				setOutput(accumulatedContent);
				localStorage.setItem(STORAGE_KEY, accumulatedContent);
			}

			localStorage.setItem(GENERATION_STATUS_KEY, "completed");
		} catch (err) {
			setError((err as Error).message);
		} finally {
			setLoading(false);
			isGenerating.current = false;
		}
	}, [authFetch, output]); // output を依存配列に含める（ステータスチェックに使用）

	useEffect(() => {
		generateOutput();
	}, [generateOutput]); // generateOutput のみを依存配列に含める

	const resetOutput = useCallback(() => {
		localStorage.removeItem(STORAGE_KEY);
		localStorage.removeItem(GENERATION_STATUS_KEY);
		setOutput("");
		setError("");
		setLoading(true);
		isGenerating.current = false;
	}, []);

	return { loading, error, output, resetOutput };
}
