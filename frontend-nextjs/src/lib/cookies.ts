import Cookies from "js-cookie";

export const setAuthCookies = (idToken: string | null) => {
	if (idToken) {
		// IDトークンをクッキーに保存
		Cookies.set("firebase-id-token", idToken, {
			expires: 14, // 14日間有効
			secure: process.env.NODE_ENV === "production",
			sameSite: "lax",
			path: "/",
		});
	} else {
		// ログアウト時にクッキーを削除
		Cookies.remove("firebase-id-token");
	}
};
