"use client";

import FileUpload from "@/features/(dashboard)/FileUpload";
import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const UploadPage: NextPage = () => {
	return (
		<div className="container mx-auto px-4 py-8">
			<h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
				ファイルアップロード
			</h1>
			<div className="max-w-xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
				<div className="p-6">
					<FileUpload />
				</div>
			</div>
		</div>
	);
};

export default withAuth(UploadPage as React.ComponentType);
