"use client";

import { setAuthCookies } from "@/lib/cookies";
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

// 認証コンテキストの型定義
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
	// ステート管理
	const [auth, setAuth] = useState<Auth | null>(null);
	const [user, setUser] = useState<User | null>(null);
	const [idToken, setIdToken] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [isInitializing, setIsInitializing] = useState(true);

	// コールバック関数の定義
	const setUserCallback = useCallback((user: User | null) => setUser(user), []);

	const setIdTokenCallback = useCallback((token: string | null) => {
		setIdToken(token);
		setAuthCookies(token);
	}, []);

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

	// 再認証処理
	const reAuthenticate = useCallback(async () => {
		if (!auth) return;

		try {
			await signOut(auth);
			setAuthCookies(null);
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
				// 永続性の設定
				await setPersistence(auth, browserLocalPersistence);
				console.log("Auth persistence set to LOCAL");

				// 現在のユーザー状態の確認と初期トークンの設定
				if (auth.currentUser) {
					const token = await auth.currentUser.getIdToken(true);
					setIdTokenCallback(token);
					setUserCallback(auth.currentUser);
				}

				// 認証状態の変更監視
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
							setIdTokenCallback(null);
						}
					} else {
						setIdTokenCallback(null);
					}
				});

				// IDトークンの変更監視
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
								"認証トークンの更新に失敗しました。再度サインインしてください。",
							);
							setIdTokenCallback(null);
							await reAuthenticate();
						}
					} else {
						setIdTokenCallback(null);
					}
				});

				// トークンの定期的な更新
				const tokenRefreshInterval = setInterval(
					async () => {
						if (auth.currentUser) {
							try {
								const newToken = await auth.currentUser.getIdToken(true);
								setIdTokenCallback(newToken);
							} catch (error) {
								console.error("Token refresh failed:", error);
								setError("トークンの更新に失敗しました");
							}
						}
					},
					30 * 60 * 1000,
				); // 30分ごとに更新

				// 初期化完了
				setIsInitializing(false);

				// クリーンアップ関数
				return () => {
					unsubscribeAuthState();
					unsubscribeIdToken();
					clearInterval(tokenRefreshInterval);
				};
			} catch (error) {
				console.error("Failed to initialize auth:", error);
				setError("認証の初期化に失敗しました。");
				setIsInitializing(false);
			}
		};

		setupAuth();
	}, [auth, setUserCallback, setIdTokenCallback, clearError, reAuthenticate]);

	// コンテキスト値の作成
	const contextValue = {
		user,
		idToken,
		error,
		setUser: setUserCallback,
		setIdToken: setIdTokenCallback,
		clearError,
		reAuthenticate,
	};

	// 初期化中は空のProviderを返す
	if (isInitializing) {
		return <AuthContext.Provider value={contextValue} />;
	}

	// 通常のレンダリング
	return (
		<AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
	);
}

// カスタムフック
export function useAuth() {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
}
