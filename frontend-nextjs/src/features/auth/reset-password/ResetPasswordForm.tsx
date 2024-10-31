"use client";

import { firebaseConfig } from "@/lib/firebase";
import { Button, Input, Typography } from "@material-tailwind/react";
import { initializeApp } from "firebase/app";
import { getAuth, sendPasswordResetEmail } from "firebase/auth";
import { useState } from "react";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export default function ResetPasswordForm() {
	const [email, setEmail] = useState("");
	const [message, setMessage] = useState("");
	const [error, setError] = useState("");

	const handleResetPassword = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		try {
			await sendPasswordResetEmail(auth, email);
			setMessage(
				"パスワードリセット用のメールを送信しました。メールをご確認ください。",
			);
			setError("");
		} catch (error) {
			console.error("パスワードリセットエラー:", error);
			setError(
				"パスワードリセットに失敗しました。メールアドレスを確認してください。",
			);
			setMessage("");
		}
	};

	return (
		<section className="grid text-center h-screen items-center p-8">
			<div>
				<Typography variant="h3" color="blue-gray" className="mb-2">
					Password Reset
				</Typography>
				<Typography className="mb-16 text-gray-600 font-normal text-[18px]">
					リセットするメールアドレスを入力してください
				</Typography>
				<form
					onSubmit={handleResetPassword}
					className="mx-auto max-w-[24rem] text-left"
				>
					<div className="mb-6">
						<label htmlFor="email">
							<Typography
								variant="small"
								className="mb-2 block font-medium text-gray-900"
							>
								Email
							</Typography>
						</label>
						<Input
							id="email"
							color="gray"
							size="lg"
							type="email"
							name="email"
							placeholder="name@mail.com"
							className="!border-t-blue-gray-200 focus:!border-t-gray-900"
							labelProps={{
								className: "hidden",
							}}
							value={email}
							onChange={(e) => setEmail(e.target.value)}
						/>
					</div>
					{error && (
						<Typography color="red" className="mb-4">
							{error}
						</Typography>
					)}
					{message && (
						<Typography color="green" className="mb-4">
							{message}
						</Typography>
					)}
					<Button
						type="submit"
						color="gray"
						size="lg"
						className="mt-6"
						fullWidth
					>
						Reset Password
					</Button>
					<Typography
						variant="small"
						color="gray"
						className="!mt-4 text-center font-normal"
					>
						<a href="/signin" className="font-medium text-gray-900">
							サインインページに戻る
						</a>
					</Typography>
				</form>
			</div>
		</section>
	);
}
