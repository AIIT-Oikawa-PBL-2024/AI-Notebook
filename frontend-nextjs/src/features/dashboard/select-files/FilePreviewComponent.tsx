import { XMarkIcon } from "@heroicons/react/24/outline";
import {
	Dialog,
	DialogBody,
	DialogHeader,
	IconButton,
} from "@material-tailwind/react";
import { useEffect, useState } from "react";
import type React from "react";

interface FilePreviewProps {
	fileName: string;
	url: string;
	contentType: string;
	onClose: () => void;
	open: boolean;
}

export default function FilePreviewComponent({
	fileName,
	url,
	contentType,
	onClose,
	open,
}: FilePreviewProps) {
	const [loadError, setLoadError] = useState<string | null>(null);

	useEffect(() => {
		// デバッグ用のログ追加
		if (open) {
			console.log("FilePreview Component Props:", {
				fileName,
				url,
				contentType,
				open,
			});

			// URLが有効かチェック
			fetch(url, { method: "HEAD" })
				.then((response) => {
					console.log("URL Check Response:", {
						ok: response.ok,
						status: response.status,
						contentType: response.headers.get("content-type"),
					});
				})
				.catch((error) => {
					console.error("URL Check Error:", error);
				});
		}
	}, [open, fileName, url, contentType]);

	const handleMediaError = (e: React.SyntheticEvent<HTMLMediaElement>) => {
		console.error("メディア読み込みエラー:", e);
		setLoadError("メディアの読み込みに失敗しました");
	};

	const renderPreview = () => {
		if (loadError) {
			return <div className="p-4 text-red-500">{loadError}</div>;
		}

		if (contentType === "application/pdf") {
			return (
				<iframe
					src={url}
					className="w-full h-[80vh]"
					title={fileName}
					onError={() => setLoadError("PDFの読み込みに失敗しました")}
				/>
			);
		}

		if (contentType.startsWith("image/")) {
			return (
				<img
					src={url}
					alt={fileName}
					className="max-w-full h-auto"
					onError={() => setLoadError("画像の読み込みに失敗しました")}
				/>
			);
		}

		if (contentType.startsWith("video/")) {
			return (
				<video controls className="w-full" onError={handleMediaError}>
					<source src={url} type={contentType} />
					<track
						kind="captions"
						srcLang="ja"
						label="Japanese captions"
						src="captions.vtt" // 仮のパスを指定
						default
					/>
					お使いのブラウザはこのビデオ形式をサポートしていません。
				</video>
			);
		}

		if (contentType.startsWith("audio/")) {
			return (
				<audio controls className="w-full" onError={handleMediaError}>
					<source src={url} type={contentType} />
					<track
						kind="captions"
						srcLang="ja"
						label="Japanese captions"
						src="captions.vtt" // 仮のパスを指定
						default
					/>
					お使いのブラウザはこのオーディオ形式をサポートしていません。
				</audio>
			);
		}

		return <div className="p-4">このファイル形式は表示できません</div>;
	};

	return (
		<Dialog
			open={open}
			handler={onClose}
			animate={{
				mount: { scale: 1, y: 0 },
				unmount: { scale: 0.9, y: -100 },
			}}
			size="xl"
		>
			<DialogHeader className="flex justify-between items-center">
				<h5 className="font-bold truncate">{fileName}</h5>
				<IconButton
					color="blue-gray"
					size="sm"
					variant="text"
					onClick={onClose}
					aria-label="閉じる"
				>
					<XMarkIcon strokeWidth={2} className="h-5 w-5" />
				</IconButton>
			</DialogHeader>
			<DialogBody divider className="p-0 overflow-auto max-h-[80vh]">
				{url ? renderPreview() : <div className="p-4">URLが見つかりません</div>}
			</DialogBody>
		</Dialog>
	);
}
