"use client";

import { getFirebaseAuth } from "@/lib/firebase";
import {
	type Auth,
	type User,
	browserLocalPersistence,
	onAuthStateChanged,
	onIdTokenChanged,
	setPersistence,
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
export const AuthContext = createContext<AuthContextType | undefined>(
	undefined,
);

// 認証プロバイダーコンポーネント
export function AuthProvider({ children }: { children: React.ReactNode }) {
	// ユーザーと IDトークンの状態管理
	const [auth, setAuth] = useState<Auth | null>(null);
	const [user, setUser] = useState<User | null>(null);
	const [idToken, setIdToken] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [isInitializing, setIsInitializing] = useState(true);

	const setUserCallback = useCallback((user: User | null) => setUser(user), []);
	const setIdTokenCallback = useCallback(
		(token: string | null) => setIdToken(token),
		[],
	);
	const clearError = useCallback(() => setError(null), []);

	// 認証インスタンスの初期化
	useEffect(() => {
		try {
			const authInstance = getFirebaseAuth();
			setAuth(authInstance);
		} catch (error) {
			console.error("Failed to initialize Firebase Auth:", error);
			setError("認証の初期化に失敗しました。");
		}
	}, []);

	const reAuthenticate = useCallback(async () => {
		if (!auth) return;

		try {
			await signOut(auth);
		} catch (error) {
			console.error("Re-authentication failed:", error);
			setError("再認証プロセスでエラーが発生しました。");
		}
	}, [auth]);

	// 認証状態の監視設定
	useEffect(() => {
		if (!auth) return;

		const setupAuth = async () => {
			try {
				await setPersistence(auth, browserLocalPersistence);
				console.log("Auth persistence set to LOCAL");

				// 現在のユーザー状態の確認
				if (auth.currentUser) {
					const token = await auth.currentUser.getIdToken(true);
					setIdTokenCallback(token);
					setUserCallback(auth.currentUser);
				}

				// Auth State Listener
				const unsubscribeAuthState = onAuthStateChanged(auth, async (user) => {
					console.log("Auth state changed. User:", user?.email);
					setUserCallback(user);

					if (user) {
						try {
							const token = await user.getIdToken();
							setIdTokenCallback(token);
							clearError();
						} catch (error) {
							console.error("Failed to get ID token:", error);
							setError("IDトークンの取得に失敗しました。");
						}
					} else {
						setIdTokenCallback(null);
					}
				});

				// ID Token Listener
				const unsubscribeIdToken = onIdTokenChanged(auth, async (user) => {
					console.log("ID token changed. User:", user?.email);
					if (user) {
						try {
							const token = await user.getIdToken();
							setIdTokenCallback(token);
							clearError();
						} catch (error) {
							console.error("Failed to get new ID token:", error);
							setError(
								"認証トークンの更新に失敗しました。再度サインインしてください",
							);
							await reAuthenticate();
						}
					} else {
						setIdTokenCallback(null);
					}
				});

				// 初期化完了
				setIsInitializing(false);

				return () => {
					unsubscribeAuthState();
					unsubscribeIdToken();
				};
			} catch (error) {
				console.error("Failed to initialize auth:", error);
				setError("認証の初期化に失敗しました。");
				setIsInitializing(false);
			}
		};

		setupAuth();
	}, [auth, setUserCallback, setIdTokenCallback, clearError, reAuthenticate]);

	const contextValue = {
		user,
		idToken,
		error,
		setUser: setUserCallback,
		setIdToken: setIdTokenCallback,
		clearError,
		reAuthenticate,
	};

	// 初期化中は空のProviderを返す（childrenはレンダリングしない）
	if (isInitializing) {
		return <AuthContext.Provider value={contextValue} />;
	}

	return (
		<AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
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
