import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useState } from "react";

const BACKEND_DEV_API_URL_OUTPUTS = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/outputs/request_stream`;

export const useOutputContent = () => {
	const [contents, setContents] = useState<string>("");
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string>("");

	const authFetch = useAuthFetch();

	const fetchOutputContent = useCallback(
		async (fileNames: string[]) => {
			setLoading(true);
			setError("");
			setContents(""); // リセット

			try {
				const response = await authFetch(BACKEND_DEV_API_URL_OUTPUTS, {
					method: "POST",
					body: JSON.stringify(fileNames),
					headers: {
						Accept: "application/json",
						"Content-Type": "application/json",
					},
				});

				if (!response.ok) {
					throw new Error("AI出力の作成に失敗しました。");
				}

				const reader = response.body?.getReader();
				const decoder = new TextDecoder("utf-8");

				if (!reader) {
					throw new Error("Failed to get reader.");
				}

				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					const chunk = decoder.decode(value);
					setContents((prevContent) => prevContent + chunk);
				}
			} catch (err) {
				setError("AI出力の作成に失敗しました。");
			} finally {
				setLoading(false);
			}
		},
		[authFetch],
	);

	return { contents, loading, error, fetchOutputContent };
};
