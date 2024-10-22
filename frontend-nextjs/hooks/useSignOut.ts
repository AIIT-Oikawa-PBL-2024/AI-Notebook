"use client";

import { getAuth, signOut } from "firebase/auth";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

export const useSignOut = () => {
	const [error, setError] = useState<string | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const router = useRouter();

	const clearSessionAndCache = useCallback(async () => {
		// ローカルストレージをクリア（Firebaseトークンを含む）
		localStorage.clear();
		// セッションストレージをクリア
		sessionStorage.clear();

		// クッキーをクリア
		const cookies = document.cookie.split(";");
		for (const cookie of cookies) {
			const [name] = cookie.trim().split("=");
			document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;`;
		}

		// アプリケーションキャッシュをクリア
		if ("caches" in window) {
			try {
				const keys = await caches.keys();
				for (const key of keys) {
					await caches.delete(key);
				}
			} catch (err) {
				console.error("キャッシュのクリアに失敗しました:", err);
			}
		}
	}, []);

	const signOutUser = useCallback(async () => {
		const auth = getAuth();
		setIsLoading(true);
		setError(null);

		try {
			await signOut(auth);
			await clearSessionAndCache();
			router.push("/signin");
		} catch (err) {
			setError("サインアウト中にエラーが発生しました。");
			console.error("サインアウトエラー:", err);
		} finally {
			setIsLoading(false);
		}
	}, [router, clearSessionAndCache]);

	return { signOutUser, error, isLoading };
};
