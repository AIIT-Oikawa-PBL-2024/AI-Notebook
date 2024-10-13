"use client";

import { type User, getAuth, onAuthStateChanged } from "firebase/auth";
import { createContext, useContext, useEffect, useState } from "react";
import type React from "react";
import { initFirebase } from "../lib/firebase";

// 認証コンテキストの型定義
interface AuthContextType {
	user: User | null;
	idToken: string | null;
	setUser: (user: User | null) => void;
	setIdToken: (token: string | null) => void;
}

// 認証コンテキストの作成
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 認証プロバイダーコンポーネント
export function AuthProvider({ children }: { children: React.ReactNode }) {
	// ユーザーと IDトークンの状態管理
	const [user, setUser] = useState<User | null>(null);
	const [idToken, setIdToken] = useState<string | null>(null);

	useEffect(() => {
		// Firebaseの初期化
		initFirebase();
		const auth = getAuth();

		// 認証状態の変更を監視
		const unsubscribe = onAuthStateChanged(auth, async (user) => {
			setUser(user);
			if (user) {
				// ユーザーがログインしている場合、IDトークンを取得
				const token = await user.getIdToken();
				setIdToken(token);
			} else {
				// ユーザーがログアウトしている場合、IDトークンをクリア
				setIdToken(null);
			}
		});

		// コンポーネントのアンマウント時にリスナーを解除
		return () => unsubscribe();
	}, []);

	// コンテキストプロバイダーを返す
	return (
		<AuthContext.Provider value={{ user, idToken, setUser, setIdToken }}>
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
