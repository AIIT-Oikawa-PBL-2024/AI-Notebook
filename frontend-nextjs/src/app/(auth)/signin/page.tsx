// SignInPage.tsx
import { BackgroundCard } from "@/components/layouts/BackgroundCard";
import { SignInForm } from "@/features/auth/signin/SignInForm";
import type React from "react";

const SignInPage: React.FC = () => {
	return (
		<main className="flex min-h-screen justify-center items-center bg-gray-100 p-4">
			<div className="flex bg-gray max-w-5xl w-full">
				{/* 左側の画像カード モバイルでは非表示 */}
				<div className="hidden md:flex md:w-1/2 p-6 items-center">
					<BackgroundCard />
				</div>
				{/* 右側のサインインフォーム モバイルでは全幅 */}
				<div className="w-full md:w-1/2 p-6 flex items-center">
					<SignInForm />
				</div>
			</div>
		</main>
	);
};

export default SignInPage;
