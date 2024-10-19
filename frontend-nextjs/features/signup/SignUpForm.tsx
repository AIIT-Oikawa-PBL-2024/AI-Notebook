"use client";

import { useAuth } from "@/providers/AuthProvider";
import { firebaseConfig } from "@/lib/firebase";
import { EyeIcon, EyeSlashIcon } from "@heroicons/react/24/solid";
import {
	Button,
	Card,
	IconButton,
	Input,
	Typography,
} from "@material-tailwind/react";
import { initializeApp } from "firebase/app";
import {
	GoogleAuthProvider,
	createUserWithEmailAndPassword,
	getAuth,
	sendEmailVerification,
	signInWithPopup,
} from "firebase/auth";
import Link from "next/link";
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

export function SignUpForm() {
	const [passwordShown, setPasswordShown] = useState(false);
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const [emailError, setEmailError] = useState<string | null>(null);
	const [passwordError, setPasswordError] = useState<string | null>(null);
	const [verificationSent, setVerificationSent] = useState(false);
	const router = useRouter();
	const { setUser } = useAuth();

	const validateEmail = (email: string) => {
		const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
		if (!re.test(email)) {
			setEmailError("有効なメールアドレスを入力してください。");
			return false;
		}
		const domain = email.split("@")[1];
		if (ALLOWED_DOMAINS.length > 0 && !ALLOWED_DOMAINS.includes(domain)) {
			setEmailError("このドメインのメールアドレスは許可されていません。");
			return false;
		}
		setEmailError(null);
		return true;
	};

	const validatePassword = (password: string) => {
		const re = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
		if (!re.test(password)) {
			setPasswordError("パスワードは英数字を含む8文字以上で入力してください。");
			return false;
		}
		setPasswordError(null);
		return true;
	};

	const handleEmailSignUp = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);

		if (!validateEmail(email) || !validatePassword(password)) {
			return;
		}

		try {
			const userCredential = await createUserWithEmailAndPassword(
				auth,
				email,
				password,
			);
			await sendEmailVerification(userCredential.user);
			setUser(userCredential.user);
			console.log("Signed up with email and password successfully");
			setVerificationSent(true);
		} catch (error) {
			console.error("サインアップエラー:", error);
			setError(
				"アカウントの作成に失敗しました。メールアドレスとパスワードを確認してください",
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

	const togglePasswordVisibility = () => {
		setPasswordShown(!passwordShown);
	};

	if (verificationSent) {
		return (
			<Card color="transparent" shadow={false}>
				<Typography variant="h4" color="blue-gray">
					Email Verification Sent
				</Typography>
				<Typography color="gray" className="mt-1 font-normal">
					確認メールを送信しました。メールを確認し、リンクをクリックして登録を完了してください。
				</Typography>
				<Button
					className="mt-6"
					fullWidth
					onClick={() => router.push("/signin")}
				>
					サインインページへ
				</Button>
			</Card>
		);
	}

	return (
		<Card color="transparent" shadow={false}>
			<Typography variant="h3" color="blue-gray" className="mb-2">
				Sign Up
			</Typography>
			<Typography color="gray" className="mt-1 font-normal">
				アカウントを作成してください
			</Typography>
			<form
				className="mt-8 mb-2 w-80 max-w-screen-lg sm:w-96"
				onSubmit={handleEmailSignUp}
			>
				<div className="mb-1 flex flex-col gap-6">
					<Typography variant="h6" color="blue-gray" className="-mb-3">
						Your Email
					</Typography>
					<Input
						size="lg"
						placeholder="name@mail.com"
						className="!border-t-blue-gray-200 focus:!border-t-gray-900"
						labelProps={{
							className: "before:content-none after:content-none",
						}}
						containerProps={{
							className: "min-w-0",
						}}
						value={email}
						onChange={(e) => {
							setEmail(e.target.value);
							validateEmail(e.target.value);
						}}
					/>
					{emailError && (
						<Typography color="red" className="mt-2 text-sm font-normal">
							{emailError}
						</Typography>
					)}
					<Typography variant="h6" color="blue-gray" className="-mb-3">
						Password
					</Typography>
					<div className="relative">
						<Input
							type={passwordShown ? "text" : "password"}
							size="lg"
							placeholder="********"
							className="!border-t-blue-gray-200 focus:!border-t-gray-900"
							labelProps={{
								className: "before:content-none after:content-none",
							}}
							containerProps={{
								className: "min-w-0",
							}}
							value={password}
							onChange={(e) => {
								setPassword(e.target.value);
								validatePassword(e.target.value);
							}}
						/>
						<IconButton
							variant="text"
							size="sm"
							className="!absolute right-1 top-1"
							onClick={togglePasswordVisibility}
						>
							{passwordShown ? (
								<EyeSlashIcon className="h-4 w-4" />
							) : (
								<EyeIcon className="h-4 w-4" />
							)}
						</IconButton>
					</div>
					{passwordError && (
						<Typography color="red" className="mt-2 text-sm font-normal">
							{passwordError}
						</Typography>
					)}
				</div>
				{error && (
					<Typography color="red" className="mt-2 text-center font-normal">
						{error}
					</Typography>
				)}
				<Button className="mt-6" fullWidth type="submit">
					Sign Up
				</Button>
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
				<Typography color="gray" className="mt-4 text-center font-normal">
					アカウント作成済みの方は{" "}
					<Link href="/signin" className="font-medium text-gray-900">
						サインインへ
					</Link>
				</Typography>
			</form>
		</Card>
	);
}
