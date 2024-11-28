import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// 保護されたルートを定義
const protectedRoutes = [
	"/ai-exercise",
	"/ai-output",
	"/notebook",
	"/select-files",
];

// 認証が不要なパブリックルートを定義
const publicRoutes = ["/signin", "/signup", "/reset-password"];

export async function middleware(request: NextRequest) {
	const { pathname } = request.nextUrl;

	// App Router形式のグループルーティングを考慮したパスの正規化
	const normalizedPathname = pathname.replace(
		/^\/(\(dashboard\)|\(auth\))/,
		"",
	);

	// セッションCookieを取得
	const idToken = request.cookies.get("firebase-id-token")?.value;

	// 現在のルートが保護されたルートかチェック
	const isProtectedRoute = protectedRoutes.some((route) =>
		normalizedPathname.startsWith(route),
	);

	// 公開ルートかチェック
	const isPublicRoute = publicRoutes.some((route) =>
		normalizedPathname.startsWith(route),
	);

	// 保護されたルートにアクセスしようとしている場合
	if (isProtectedRoute) {
		// 認証されていない場合、サインインページにリダイレクト
		if (!idToken) {
			const redirectUrl = new URL("/signin", request.url);
			return NextResponse.redirect(redirectUrl);
		}
	}

	// サインインページなどの認証ページにアクセスしようとしている場合
	if (isPublicRoute && idToken) {
		// すでに認証済みの場合、トップページにリダイレクト
		return NextResponse.redirect(new URL("/", request.url));
	}

	// その他のケースは通常通り処理を続行
	return NextResponse.next();
}

// ミドルウェアを適用するパスを設定
// App Routerのグループルーティングを考慮したmatcherの設定
export const config = {
	matcher: [
		// (dashboard)グループ内のルートを保護
		"/(dashboard)/:path*",
		// 認証関連のパス(auth)グループのルートも確認
		"/(auth)/:path*",
		// 以下は除外
		"/((?!api/auth|_next/static|_next/image|favicon.ico).*)",
	],
};
