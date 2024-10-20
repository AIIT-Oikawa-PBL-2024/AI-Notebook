"use client";

import { initFirebase } from "@/lib/firebase";
import {
	type User,
	getAuth,
	onAuthStateChanged,
	onIdTokenChanged,
	signOut,
} from "firebase/auth";
import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useState,
} from "react";
import type React from "react";

// 認証コンテキストの型定義を拡張
interface AuthContextType {
	user: User | null;
	idToken: string | null;
	error: string | null;
	setUser: (user: User | null) => void;
	setIdToken: (token: string | null) => void;
	clearError: () => void;
	reAuthenticate: () => Promise<void>;
}

// 認証コンテキストの作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 認証プロバイダーコンポーネント
export function AuthProvider({ children }: { children: React.ReactNode }) {
	// ユーザーと IDトークンの状態管理
	const [user, setUser] = useState<User | null>(null);
	const [idToken, setIdToken] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	const setUserCallback = useCallback((user: User | null) => setUser(user), []);
	const setIdTokenCallback = useCallback(
		(token: string | null) => setIdToken(token),
		[],
	);

	const clearError = useCallback(() => setError(null), []);

	const reAuthenticate = useCallback(async () => {
		const auth = getAuth();
		try {
			await signOut(auth);
			setError("認証トークンの更新に失敗しました。再度サインインしてください");
			// ここで再認証用のUIを表示するか、ログインページにリダイレクトします
		} catch (error) {
			setError("再認証プロセスでエラーが発生しました。");
		}
	}, []);

	useEffect(() => {
		// Firebaseの初期化
		initFirebase();
		const auth = getAuth();

		// 認証状態の変更を監視
		const unsubscribeAuthState = onAuthStateChanged(auth, async (user) => {
			setUserCallback(user);
			if (user) {
				try {
					// ユーザーがログインしている場合、IDトークンを取得
					const token = await user.getIdToken();
					setIdTokenCallback(token);
				} catch (error) {
					console.error("Failed to get ID token:", error);
					setError("IDトークンの取得に失敗しました。");
				}
			} else {
				// ユーザーがログアウトしている場合、IDトークンをクリア
				setIdTokenCallback(null);
			}
		});

		// IDトークンの変更を監視（自動更新用）
		const unsubscribeIdToken = onIdTokenChanged(auth, async (user) => {
			if (user) {
				try {
					const token = await user.getIdToken();
					setIdTokenCallback(token);
					clearError(); // トークン取得に成功したらエラーをクリア
				} catch (error) {
					console.error("Failed to get new ID token:", error);
					setError(
						"認証トークンの更新に失敗しました。再度サインインしてください",
					);
					reAuthenticate();
				}
			} else {
				setIdTokenCallback(null);
			}
		});

		// コンポーネントのアンマウント時にリスナーを解除
		return () => {
			unsubscribeAuthState();
			unsubscribeIdToken();
		};
	}, [setUserCallback, setIdTokenCallback, clearError, reAuthenticate]);

	// コンテキストプロバイダーを返す
	return (
		<AuthContext.Provider
			value={{
				user,
				idToken,
				error,
				setUser: setUserCallback,
				setIdToken: setIdTokenCallback,
				clearError,
				reAuthenticate,
			}}
		>
			{children}
		</AuthContext.Provider>
	);
}

// カスタムフック: 認証コンテキストを使用するためのフック
export function useAuth() {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
}
