"use client";

import FileUpload from "@/features/(dashboard)/FileUpload";
import { useSignOut } from "@/hooks/useSignOut";
import { useAuth } from "@/providers/AuthProvider";
import { withAuth } from "@/utils/withAuth";
import { Button } from "@material-tailwind/react";
import type { NextPage } from "next";

const UploadPage: NextPage = () => {
	const { user } = useAuth();
	const { signOutUser, error, isLoading } = useSignOut();

	return (
		<div className="container mx-auto px-4 py-8">
			<h1 className="text-3xl font-bold mb-6 text-center text-gray-800">
				ファイルアップロード
			</h1>
			{user && (
				<div className="mb-6 text-center text-gray-600">
					<p>ユーザー: {user.displayName || user.email}</p>
					<Button onClick={signOutUser} disabled={isLoading}>
						{isLoading ? "サインアウト中..." : "サインアウト"}
					</Button>
					{error && <p className="text-red-500 mt-2">{error}</p>}
				</div>
			)}
			<div className="max-w-xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
				<div className="p-6">
					<FileUpload />
				</div>
			</div>
		</div>
	);
};

export default withAuth(UploadPage as React.ComponentType);
