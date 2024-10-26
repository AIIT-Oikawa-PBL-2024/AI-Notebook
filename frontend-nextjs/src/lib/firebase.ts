// app/lib/firebase.ts
// Firebase SDKからの必要なモジュールのインポート
import { getApps, initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Firebase設定
export const firebaseConfig = {
	// 環境変数から Firebase 設定を読み込む
	apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
	authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
	projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
	storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
	messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
	appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Firebase初期化関数
export const initFirebase = () => {
	// アプリが初期化されていない場合のみ初期化を行う
	if (!getApps().length) {
		const app = initializeApp(firebaseConfig);
		return app;
	}
};

// Firebase認証インスタンスを取得する関数
export const getFirebaseAuth = () => {
	// Firebaseを初期化し、認証インスタンスを返す
	initFirebase();
	return getAuth();
};
