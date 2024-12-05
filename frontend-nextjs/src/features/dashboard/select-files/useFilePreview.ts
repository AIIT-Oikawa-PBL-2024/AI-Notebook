import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useCallback, useState } from "react";

interface FilePreviewData {
	fileName: string;
	url: string;
	contentType: string;
}

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_SIGNED_URL = `${BACKEND_HOST}/files/generate_download_signed_url`;

const getContentType = (fileName: string): string => {
	const extension = fileName.split(".").pop()?.toLowerCase() || "";
	const contentTypes: { [key: string]: string } = {
		pdf: "application/pdf",
		png: "image/png",
		jpg: "image/jpeg",
		jpeg: "image/jpeg",
		mp4: "video/mp4",
		mp3: "audio/mpeg",
		wav: "audio/wav",
	};
	return contentTypes[extension] || "application/octet-stream";
};

export const useFilePreview = () => {
	const [previewUrls, setPreviewUrls] = useState<{
		[key: string]: FilePreviewData;
	}>({});
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const authFetch = useAuthFetch();

	const generatePreviewUrl = useCallback(
		async (fileNames: string[]) => {
			setLoading(true);
			setError(null);

			try {
				console.log("Generating preview URLs for:", fileNames);

				const response = await authFetch(BACKEND_API_URL_SIGNED_URL, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(fileNames),
				});

				if (!response.ok) {
					const errorData = await response.json();
					throw new Error(
						errorData.detail || "署名付きURLの生成に失敗しました",
					);
				}

				const urls = await response.json();
				console.log("Generated URLs response:", urls);

				// フルパスのファイル名からファイル名のみを抽出する関数
				const getBaseName = (fullPath: string): string => {
					const parts = fullPath.split("/");
					return parts[parts.length - 1];
				};

				const newPreviewUrls = Object.entries(urls).reduce(
					(acc: { [key: string]: FilePreviewData }, [fullPath, url]) => {
						const fileName = getBaseName(fullPath);
						acc[fileName] = {
							fileName,
							url: url as string,
							contentType: getContentType(fileName),
						};
						return acc;
					},
					{},
				);

				console.log("Processed preview URLs:", newPreviewUrls);
				setPreviewUrls(newPreviewUrls);
			} catch (err) {
				console.error("Error generating preview URL:", err);
				setError(
					err instanceof Error ? err.message : "予期せぬエラーが発生しました",
				);
			} finally {
				setLoading(false);
			}
		},
		[authFetch],
	);

	const clearPreviews = useCallback(() => {
		setPreviewUrls({});
		setError(null);
	}, []);

	return {
		previewUrls,
		loading,
		error,
		generatePreviewUrl,
		clearPreviews,
	};
};
