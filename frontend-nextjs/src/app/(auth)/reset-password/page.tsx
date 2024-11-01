import { BackgroundCard } from "@/components/layouts/BackgroundCard";
import ResetPasswordForm from "@/features/auth/reset-password/ResetPasswordForm";

const ResetPasswordPage = () => {
	return (
		<main className="flex min-h-screen justify-center items-center bg-gray-100 p-4">
			<div className="flex bg-gray max-w-5xl w-full">
				{/* 左側の画像カード モバイルでは非表示 */}
				<div className="hidden md:flex md:w-1/2 p-6 items-center">
					<BackgroundCard />
				</div>
				{/* 右側のサインインフォーム モバイルでは全幅 */}
				<div className="w-full md:w-1/2 p-6 flex items-center">
					<ResetPasswordForm />
				</div>
			</div>
		</main>
	);
};
export default ResetPasswordPage;
