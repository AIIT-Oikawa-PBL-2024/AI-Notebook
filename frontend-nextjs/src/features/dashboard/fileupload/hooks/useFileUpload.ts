import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { useState } from "react";

interface FileInfo {
	name: string;
	size: number;
	type: string;
	file: File;
}

interface UseFileUploadReturn {
	uploadFiles: (files: FileInfo[]) => Promise<boolean>;
	isUploading: boolean;
}

export const useFileUpload = (): UseFileUploadReturn => {
	const { user } = useAuth();
	const authFetch = useAuthFetch();
	const [isUploading, setIsUploading] = useState<boolean>(false);

	const BACKEND_DEV_API_URL_SIGNEDURL = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/files/generate_upload_signed_url/`;
	const BACKEND_DEV_API_URL_REGISTERFILES = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/files/register_files/`;

	const uploadFiles = async (files: FileInfo[]): Promise<boolean> => {
		if (!user) {
			throw new Error("User is not authenticated");
		}

		setIsUploading(true);
		try {
			// 1. Get signed URLs
			const filenames = files.map((file) => file.name);
			const response = await authFetch(BACKEND_DEV_API_URL_SIGNEDURL, {
				method: "POST",
				body: JSON.stringify(filenames),
				headers: {
					Accept: "application/json",
					"Content-Type": "application/json",
				},
			});

			if (!response.ok) {
				throw new Error("Failed to get signed URLs");
			}

			const data = await response.json();

			// 2. Upload files
			for (const file of files) {
				const orgFileName = file.name;
				const normalizedFileName = `${user.uid}/${file.name}`.normalize("NFC");
				const signedUrl = data[normalizedFileName];

				// Upload to signed URL
				const uploadResponse = await fetch(signedUrl, {
					method: "PUT",
					body: file.file,
					headers: {
						"Content-Type": "application/octet-stream",
					},
				});

				if (!uploadResponse.ok) {
					throw new Error("Failed to upload file");
				}

				// Register file
				const formData = new FormData();
				formData.append("files", file.file, orgFileName);
				const registerResponse = await authFetch(
					BACKEND_DEV_API_URL_REGISTERFILES,
					{
						method: "POST",
						body: formData,
						headers: {
							Accept: "application/json",
						},
					},
				);

				if (!registerResponse.ok) {
					throw new Error("Failed to register file");
				}
			}

			return true;
		} catch (error) {
			console.error("Upload error:", error);
			throw error;
		} finally {
			setIsUploading(false);
		}
	};

	return {
		uploadFiles,
		isUploading,
	};
};
