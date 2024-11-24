import { ButtonWithIcon } from "@/features/dashboard/fileupload/Button";
import { useFileUpload } from "@/features/dashboard/fileupload/hooks/useFileUpload";
import type React from "react";
import { type ChangeEvent, type DragEvent, useRef, useState } from "react";

interface FileInfo {
	name: string;
	size: number;
	type: string;
	file: File;
}

const FileUploadComponent: React.FC = () => {
	const [files, setFiles] = useState<FileInfo[]>([]);
	const [isDragActive, setIsDragActive] = useState<boolean>(false);
	const [errorMessage, setErrorMessage] = useState<string>("");
	const fileInputRef = useRef<HTMLInputElement>(null);
	const { uploadFiles, isUploading } = useFileUpload();

	const isAllowedFile = (file: File): boolean => {
		const allowedTypes = [
			"application/pdf",
			"image/png",
			"image/jpeg",
			"video/mp4",
			"audio/mpeg",
			"audio/wav",
		];
		const allowedExtensions = [
			".pdf",
			".png",
			".jpg",
			".jpeg",
			".mp4",
			".mp3",
			".wav",
		];
		return (
			allowedTypes.includes(file.type) ||
			allowedExtensions.some((ext) => file.name.toLowerCase().endsWith(ext))
		);
	};

	const handleDrag = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		if (e.type === "dragenter" || e.type === "dragover") {
			setIsDragActive(true);
		} else if (e.type === "dragleave") {
			setIsDragActive(false);
		}
	};

	const handleDrop = (e: DragEvent<HTMLDivElement>) => {
		e.preventDefault();
		e.stopPropagation();
		setIsDragActive(false);
		if (e.dataTransfer.files?.[0]) {
			handleFiles(e.dataTransfer.files);
		}
	};

	const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
		e.preventDefault();
		if (e.target.files?.[0]) {
			handleFiles(e.target.files);
		}
	};

	const handleFiles = (fileList: FileList) => {
		const newFiles = Array.from(fileList)
			.filter((file) => {
				if (isAllowedFile(file)) {
					return true;
				}
				setErrorMessage(
					`${file.name} は許可されていないファイル形式です。PDF、PNG、JPEG、MP4、MP3、WAVファイルのみアップロード可能です。`,
				);
				setTimeout(() => setErrorMessage(""), 5000);
				return false;
			})
			.map((file) => ({
				name: file.name,
				size: file.size,
				type: file.type,
				file: file,
			}));

		setFiles((prevFiles) => [...prevFiles, ...newFiles]);
	};

	const onButtonClick = () => {
		fileInputRef.current?.click();
	};

	const removeFile = (index: number) => {
		setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
	};

	const handleUpload = async () => {
		try {
			const success = await uploadFiles(files);
			if (success) {
				alert("ファイルが正常にアップロードされました");
				setFiles([]);
			} else {
				alert("ファイルのアップロードに失敗しました");
			}
		} catch (error) {
			alert(
				`エラー: ${error instanceof Error ? error.message : "不明なエラーが発生しました"}`,
			);
		}
	};

	const getFileIcon = (fileType: string) => {
		if (fileType.startsWith("image/")) {
			return (
				<svg
					xmlns="http://www.w3.org/2000/svg"
					className="h-5 w-5 text-blue-500"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<title>Image file icon</title>
					<path
						fillRule="evenodd"
						d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"
						clipRule="evenodd"
					/>
				</svg>
			);
		}
		return (
			<svg
				xmlns="http://www.w3.org/2000/svg"
				className="h-5 w-5 text-red-500"
				viewBox="0 0 20 20"
				fill="currentColor"
			>
				<title>Document file icon</title>
				<path
					fillRule="evenodd"
					d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z"
					clipRule="evenodd"
				/>
			</svg>
		);
	};

	return (
		<div className="container mx-auto p-4">
			<div
				className={`p-10 border-2 border-dashed rounded-lg text-center cursor-pointer transition-colors ${
					isDragActive
						? "border-blue-400 bg-blue-100"
						: "border-gray-300 hover:border-gray-400"
				}`}
				onDragEnter={handleDrag}
				onDragLeave={handleDrag}
				onDragOver={handleDrag}
				onDrop={handleDrop}
				onClick={onButtonClick}
				onKeyUp={(e) => {
					if (e.key === "Enter" || e.key === " ") {
						onButtonClick();
					}
				}}
			>
				<input
					ref={fileInputRef}
					type="file"
					multiple
					accept=".pdf,.png,.jpg,.jpeg,.mp4,.mp3,.wav"
					onChange={handleChange}
					className="hidden"
				/>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					className="h-12 w-12 mx-auto text-gray-400"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<title>Upload icon</title>
					<path
						fillRule="evenodd"
						d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z"
						clipRule="evenodd"
					/>
				</svg>
				<p className="mt-2 text-sm text-gray-500">
					PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください
				</p>
			</div>

			{errorMessage && (
				<div className="mt-4 p-2 bg-red-100 border border-red-400 text-red-700 rounded flex items-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						className="h-5 w-5 mr-2"
						viewBox="0 0 20 20"
						fill="currentColor"
					>
						<title>Error icon</title>
						<path
							fillRule="evenodd"
							d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
							clipRule="evenodd"
						/>
					</svg>
					<span>{errorMessage}</span>
				</div>
			)}

			{files.length > 0 && (
				<div className="mt-6">
					<h4 className="text-lg font-semibold mb-2">
						アップロードするファイル:
					</h4>
					<ul className="space-y-2">
						{files.map((file, index) => (
							<li
								key={file.name}
								className="flex items-center justify-between bg-gray-100 p-2 rounded"
							>
								<div className="flex items-center">
									{getFileIcon(file.type)}
									<span className="text-sm font-medium text-gray-700 ml-2">
										{file.name}
									</span>
									<span className="text-xs text-gray-500 ml-2">
										({file.size} bytes)
									</span>
								</div>
								<button
									type="button"
									onClick={() => removeFile(index)}
									className="text-red-500 hover:text-red-700"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										className="h-5 w-5"
										viewBox="0 0 20 20"
										fill="currentColor"
									>
										<title>Remove file icon</title>
										<path
											fillRule="evenodd"
											d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
											clipRule="evenodd"
										/>
									</svg>
								</button>
							</li>
						))}
					</ul>
					<div className="mt-4">
						<ButtonWithIcon
							onClick={handleUpload}
							disabled={isUploading || files.length === 0}
						>
							{isUploading ? "アップロード中..." : "アップロード"}
						</ButtonWithIcon>
					</div>
				</div>
			)}
		</div>
	);
};

export default FileUploadComponent;
