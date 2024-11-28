import { middleware } from "@/middleware";
import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

// NextRequestのモック
vi.mock("next/server", async () => {
	const actual = await vi.importActual("next/server");
	return {
		...actual,
		NextResponse: {
			redirect: vi.fn().mockImplementation((url) => ({ url })),
			next: vi.fn().mockReturnValue({ type: "next" }),
		},
	};
});

describe("Middleware", () => {
	let mockRequest: NextRequest;

	beforeEach(() => {
		// テスト前にモックをリセット
		vi.clearAllMocks();

		// NextRequestのモックを作成
		mockRequest = {
			nextUrl: {
				pathname: "",
				href: "http://localhost:3000",
			},
			url: "http://localhost:3000",
			cookies: {
				get: vi.fn(),
			},
		} as unknown as NextRequest;
	});

	describe("保護されたルート", () => {
		it("認証なしで保護されたルートにアクセスした場合、サインインページにリダイレクトされる", async () => {
			// /ai-exerciseへのアクセスをテスト
			mockRequest.nextUrl.pathname = "/ai-exercise";
			mockRequest.cookies.get = vi.fn().mockReturnValue(undefined);

			await middleware(mockRequest);

			expect(NextResponse.redirect).toHaveBeenCalledWith(
				expect.objectContaining({
					href: expect.stringContaining("/signin"),
				}),
			);
		});

		it("有効な認証がある場合、保護されたルートへのアクセスが許可される", async () => {
			mockRequest.nextUrl.pathname = "/ai-exercise";
			mockRequest.cookies.get = vi
				.fn()
				.mockReturnValue({ value: "valid-token" });

			await middleware(mockRequest);

			expect(NextResponse.next).toHaveBeenCalled();
			expect(NextResponse.redirect).not.toHaveBeenCalled();
		});
	});

	describe("パブリックルート", () => {
		it("認証済みの状態でサインインページにアクセスした場合、ホームページにリダイレクトされる", async () => {
			mockRequest.nextUrl.pathname = "/signin";
			mockRequest.cookies.get = vi
				.fn()
				.mockReturnValue({ value: "valid-token" });

			await middleware(mockRequest);

			expect(NextResponse.redirect).toHaveBeenCalledWith(
				expect.objectContaining({
					href: expect.stringContaining("/"),
				}),
			);
		});

		it("未認証の状態でサインインページへのアクセスが許可される", async () => {
			mockRequest.nextUrl.pathname = "/signin";
			mockRequest.cookies.get = vi.fn().mockReturnValue(undefined);

			await middleware(mockRequest);

			expect(NextResponse.next).toHaveBeenCalled();
			expect(NextResponse.redirect).not.toHaveBeenCalled();
		});
	});

	describe("グループルーティング", () => {
		it("(dashboard)グループのルーティングが正しく処理される", async () => {
			mockRequest.nextUrl.pathname = "/(dashboard)/ai-exercise";
			mockRequest.cookies.get = vi.fn().mockReturnValue(undefined);

			await middleware(mockRequest);

			expect(NextResponse.redirect).toHaveBeenCalledWith(
				expect.objectContaining({
					href: expect.stringContaining("/signin"),
				}),
			);
		});

		it("(auth)グループのルーティングが正しく処理される", async () => {
			mockRequest.nextUrl.pathname = "/(auth)/signup";
			mockRequest.cookies.get = vi
				.fn()
				.mockReturnValue({ value: "valid-token" });

			await middleware(mockRequest);

			expect(NextResponse.redirect).toHaveBeenCalledWith(
				expect.objectContaining({
					href: expect.stringContaining("/"),
				}),
			);
		});
	});
});
