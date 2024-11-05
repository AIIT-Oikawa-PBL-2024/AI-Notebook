"use client";

import { firebaseConfig } from "@/lib/firebase";
import { useAuth } from "@/providers/AuthProvider";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/20/solid";
import { Button, Input, Typography } from "@material-tailwind/react";
import { initializeApp } from "firebase/app";
import {
	GoogleAuthProvider,
	getAuth,
	signInWithEmailAndPassword,
	signInWithPopup,
} from "firebase/auth";
import { useRouter } from "next/navigation";
import { useState } from "react";

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

// 許可されるメールアドレスのドメインを取得
const ALLOWED_DOMAINS = process.env.NEXT_PUBLIC_ALLOWED_EMAIL_DOMAINS
	? process.env.NEXT_PUBLIC_ALLOWED_EMAIL_DOMAINS.split(",").map((domain) =>
			domain.trim(),
		)
	: [];

export function SignInForm() {
	const [passwordShown, setPasswordShown] = useState(false);
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const router = useRouter();
	const { setUser } = useAuth();

	const togglePasswordVisiblity = () => setPasswordShown((cur) => !cur);

	const handleEmailSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		try {
			const userCredential = await signInWithEmailAndPassword(
				auth,
				email,
				password,
			);

			if (userCredential.user.emailVerified) {
				setUser(userCredential.user);
				console.log("Signed in successfully");
				router.push("/");
			} else {
				setError(
					"メールアドレスが確認されていません。メールを確認してアカウントを有効化してください。",
				);
			}
		} catch (error) {
			console.error("サインインエラー:", error);
			setError(
				"サインインに失敗しました。メールアドレスとパスワードを確認してください",
			);
		}
	};

	const handleGoogleSignIn = async () => {
		try {
			const result = await signInWithPopup(auth, googleProvider);
			const email = result.user.email;
			if (email && ALLOWED_DOMAINS.length > 0) {
				const domain = email.split("@")[1];
				if (!ALLOWED_DOMAINS.includes(domain)) {
					throw new Error(
						"このGoogleアカウントのドメインは許可されていません。",
					);
				}
			}
			setUser(result.user);
			console.log("Signed in with Google successfully");
			router.push("/");
		} catch (error) {
			console.error("Googleサインインエラー:", error);
			setError("サインインに失敗しました。Googleアカウントを確認してください");
		}
	};

	return (
		<section className="grid text-center h-screen items-center p-8">
			<div>
				<Typography variant="h3" color="blue-gray" className="mb-2">
					Sign In
				</Typography>
				<Typography className="mb-16 text-gray-600 font-normal text-[18px]">
					メールアドレスとパスワードを入力してください
				</Typography>
				<form
					onSubmit={handleEmailSignIn}
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
							autoComplete="email"  // メールアドレスの自動入力を有効にする
							placeholder="name@mail.com"
							className="!border-t-blue-gray-200 focus:!border-t-gray-900"
							labelProps={{
								className: "hidden",
							}}
							value={email}
							onChange={(e) => setEmail(e.target.value)}
						/>
					</div>
					<div className="mb-6">
						<label htmlFor="password">
							<Typography
								variant="small"
								className="mb-2 block font-medium text-gray-900"
							>
								Password
							</Typography>
						</label>
						<Input
							id="password"
							size="lg"
							placeholder="********"
							labelProps={{
								className: "hidden",
							}}
							className="!border-t-blue-gray-200 focus:!border-t-gray-900"
							type={passwordShown ? "text" : "password"}
							value={password}
							autoComplete="current-password"  // パスワードの自動入力を有効にする
							onChange={(e) => setPassword(e.target.value)}
							icon={
								<i
									onClick={togglePasswordVisiblity}
									onKeyUp={(e) => {
										if (e.key === "Enter") togglePasswordVisiblity();
									}}
									tabIndex={0}
									role="button"
								>
									{passwordShown ? (
										<EyeIcon className="h-5 w-5" />
									) : (
										<EyeSlashIcon className="h-5 w-5" />
									)}
								</i>
							}
						/>
					</div>
					{error && (
						<Typography color="red" className="mb-4">
							{error}
						</Typography>
					)}
					<Button
						type="submit"
						color="gray"
						size="lg"
						className="mt-6"
						fullWidth
					>
						Sign In
					</Button>
					<div className="!mt-4 flex justify-end">
						<Typography
							as="a"
							href="/reset-password"
							color="blue-gray"
							variant="small"
							className="font-medium"
						>
							パスワードを忘れた方はこちら
						</Typography>
					</div>
					<Button
						variant="outlined"
						size="lg"
						className="mt-6 flex h-12 items-center justify-center gap-2"
						fullWidth
						onClick={handleGoogleSignIn}
						aria-label="Sign in with Google"
					>
						<img
							src={"https://www.material-tailwind.com/logos/logo-google.png"}
							alt=""
							className="h-6 w-6"
						/>
						Sign in with Google
					</Button>
					<Typography
						variant="small"
						color="gray"
						className="!mt-4 text-center font-normal"
					>
						アカウント未登録の方は{" "}
						<a href="/signup" className="font-medium text-gray-900">
							サインアップへ
						</a>
					</Typography>
				</form>
			</div>
		</section>
	);
}
