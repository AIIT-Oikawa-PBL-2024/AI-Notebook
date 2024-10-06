"use client";

import { firebaseConfig } from "@/app/lib/firebase";
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

export function SignInForm() {
	const [passwordShown, setPasswordShown] = useState(false);
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState<string | null>(null);
	const router = useRouter();

	const togglePasswordVisiblity = () => setPasswordShown((cur) => !cur);

	const handleSignIn = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		try {
			await signInWithEmailAndPassword(auth, email, password);
			console.log("Signed in successfully");
			router.push("/");
		} catch (error) {
			setError((error as Error).message);
		}
	};

	const handleGoogleSignIn = async () => {
		try {
			await signInWithPopup(auth, googleProvider);
			console.log("Signed in with Google successfully");
			router.push("/");
		} catch (error) {
			setError((error as Error).message);
		}
	};

	return (
		<section className="grid text-center h-screen items-center p-8">
			<div>
				<Typography variant="h3" color="blue-gray" className="mb-2">
					Sign In
				</Typography>
				<Typography className="mb-16 text-gray-600 font-normal text-[18px]">
					Enter your email and password to sign in
				</Typography>
				<form
					onSubmit={handleSignIn}
					className="mx-auto max-w-[24rem] text-left"
				>
					<div className="mb-6">
						<label htmlFor="email">
							<Typography
								variant="small"
								className="mb-2 block font-medium text-gray-900"
							>
								Your Email
							</Typography>
						</label>
						<Input
							id="email"
							color="gray"
							size="lg"
							type="email"
							name="email"
							placeholder="name@mail.com"
							className="w-full placeholder:opacity-100 focus:border-t-primary border-t-blue-gray-200"
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
							size="lg"
							placeholder="********"
							labelProps={{
								className: "hidden",
							}}
							className="w-full placeholder:opacity-100 focus:border-t-primary border-t-blue-gray-200"
							type={passwordShown ? "text" : "password"}
							value={password}
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
							href="/forgot-password"
							color="blue-gray"
							variant="small"
							className="font-medium"
						>
							Forgot password
						</Typography>
					</div>
					<Button
						variant="outlined"
						size="lg"
						className="mt-6 flex h-12 items-center justify-center gap-2"
						fullWidth
						onClick={handleGoogleSignIn}
					>
						<img
							src={"https://www.material-tailwind.com/logos/logo-google.png"}
							alt="google"
							className="h-6 w-6"
						/>{" "}
						Sign in with Google
					</Button>
					<Typography
						variant="small"
						color="gray"
						className="!mt-4 text-center font-normal"
					>
						Not registered?{" "}
						<a href="/create-account" className="font-medium text-gray-900">
							Create account
						</a>
					</Typography>
				</form>
			</div>
		</section>
	);
}
