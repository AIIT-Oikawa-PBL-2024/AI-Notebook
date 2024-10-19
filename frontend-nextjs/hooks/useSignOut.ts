"use client";

import { getAuth, signOut } from "firebase/auth";
import { useRouter } from "next/navigation";
import { useState, useCallback } from "react";

// サインアウト機能を提供するカスタムフック
export const useSignOut = () => {
	// エラーメッセージを管理するための状態
	const [error, setError] = useState<string | null>(null);
	// ローディング状態を管理するための状態
	const [isLoading, setIsLoading] = useState(false);
	// ページ遷移のためのrouterオブジェクト
	const router = useRouter();

	// ユーザーをサインアウトさせる関数
	const signOutUser = useCallback(async () => {
		// Firebase Authenticationのインスタンスを取得
		const auth = getAuth();
		// ローディング状態を開始
		setIsLoading(true);
		// エラー状態をリセット
		setError(null);

		try {
			// Firebase のサインアウト処理を実行
			await signOut(auth);
			// サインアウト成功後、サインインページにリダイレクト
			router.push("/signin");
		} catch (err) {
			// サインアウト処理中にエラーが発生した場合
			setError("サインアウト中にエラーが発生しました。");
			console.error("サインアウトエラー:", err);
		} finally {
			// 処理が完了したらローディング状態を終了
			setIsLoading(false);
		}
	}, [router]);

	// フックの戻り値として、サインアウト関数、エラー状態、ローディング状態を返す
	return { signOutUser, error, isLoading };
};