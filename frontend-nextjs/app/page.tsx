"use client";

import { useAuth } from "@/app/components/AuthProvider";
import FileUpload from "@/app/components/FileUpload";
import { withAuth } from "@/app/components/withAuth";
import type { NextPage } from "next";
import Image from "next/image";

const UploadPage: NextPage = () => {
	const { user } = useAuth();

	return (
		<div className="container mx-auto px-4 py-8">
			<h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
				ファイルアップロード
			</h1>
			{user && (
				<div className="mb-6 text-center text-gray-600">
					ユーザー: {user.displayName || user.email}
				</div>
			)}
			<div className="max-w-xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
				<div className="p-6">
					<FileUpload />
				</div>
				<div className="mt-6">
					<Image
						src="/pbl-flyer.jpg"
						alt="アプリの説明画像"
						width={500}
						height={300}
						layout="responsive"
						className="rounded-b-lg"
					/>
				</div>
			</div>
		</div>
	);
};

export default withAuth(UploadPage as React.ComponentType);
