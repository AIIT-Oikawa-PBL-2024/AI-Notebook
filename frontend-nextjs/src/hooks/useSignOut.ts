"use client";

import { setAuthCookies } from "@/lib/cookies";
import { getAuth, signOut } from "firebase/auth";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

export const useSignOut = () => {
	const [error, setError] = useState<string | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const router = useRouter();

	const clearSessionAndCache = useCallback(async () => {
		// ローカルストレージをクリア
		localStorage.clear();

		// セッションストレージをクリア
		sessionStorage.clear();

		// Firebase認証用のクッキーを明示的にクリア
		setAuthCookies(null); // 既存の関数を使用

		// その他のクッキーをすべてクリア
		const cookies = Cookies.get();
		for (const cookieName of Object.keys(cookies)) {
			Cookies.remove(cookieName, { path: "/" });
		}

		// 従来のクッキークリア方法もバックアップとして保持
		const documentCookies = document.cookie.split(";");
		for (const cookie of documentCookies) {
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
			// サインアウト処理
			await signOut(auth);
			// セッションとキャッシュのクリア
			await clearSessionAndCache();
			// サインインページへリダイレクト
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
