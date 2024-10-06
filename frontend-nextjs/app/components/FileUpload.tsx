"use client";

import { ButtonWithIcon } from "@/app/components/Button";
import { type ChangeEvent, useRef, useState } from "react";

const ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"];
const BACKEND_DEV_API_URL = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/files/upload`;

interface UploadedFile {
	filename: string;
	message: string;
}

interface UploadResponse {
	success: boolean;
	success_files?: UploadedFile[];
	failed_files?: UploadedFile[];
	message?: string;
}

const isValidFile = (file: File): boolean => {
	const fileExt = file.name.split(".").pop()?.toLowerCase() || "";
	return ALLOWED_EXTENSIONS.includes(fileExt);
};

export default function FileUpload() {
	const [files, setFiles] = useState<File[]>([]);
	const [message, setMessage] = useState<string>("");
	const fileInputRef = useRef<HTMLInputElement>(null);

	const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
		const newFiles = Array.from(event.target.files || []).filter((file) => {
			if (isValidFile(file)) {
				return true;
			}
			setMessage(
				`${file.name}をアップロードできませんでした。PDF、JPG、JPEG、またはPNGファイルをアップロードしてください`,
			);
			return false;
		});

		setFiles((prevFiles) => {
			const uniqueFiles = newFiles.filter(
				(file) => !prevFiles.some((prevFile) => prevFile.name === file.name),
			);
			return [...prevFiles, ...uniqueFiles];
		});
	};

	const handleUpload = async () => {
		const formData = new FormData();
		for (const file of files) {
			formData.append("files", file);
		}

		try {
			const response = await fetch(BACKEND_DEV_API_URL, {
				method: "POST",
				body: formData,
				headers: {
					Accept: "application/json",
				},
			});

			const result: UploadResponse = await response.json();

			if (result.success) {
				setMessage("ファイルのアップロードが完了しました。");
				if (result.success_files) {
					for (const file of result.success_files) {
						console.log(`${file.filename}: ${file.message}`);
					}
				}
				if (result.failed_files) {
					for (const file of result.failed_files) {
						console.warn(`${file.filename}: ${file.message}`);
					}
				}
			} else {
				setMessage("ファイルのアップロードに失敗しました。");
			}
		} catch (error) {
			setMessage(`リクエストでエラーが発生しました：${error}`);
		}
	};

	const handleButtonClick = () => {
		fileInputRef.current?.click();
	};

	return (
		<div className="flex flex-col items-start gap-4">
			<input
				type="file"
				multiple
				accept=".pdf,.jpg,.jpeg,.png"
				onChange={handleFileChange}
				className="hidden"
				ref={fileInputRef}
			/>
			<ButtonWithIcon onClick={handleButtonClick}>
				ファイルを選択
			</ButtonWithIcon>
			{files.map((file) => (
				<p key={file.name}>
					アップロードボタンを押して下さい: {file.name} (Size:{" "}
					{(file.size / 1024 / 1024).toFixed(2)} MB)
				</p>
			))}
			{files.length > 0 && (
				<ButtonWithIcon onClick={handleUpload}>アップロード</ButtonWithIcon>
			)}
			{message && <p>{message}</p>}
		</div>
	);
}
