import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// useAuthフックをモック化します
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

// グローバルなfetch関数をモック化します
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

// useAuthFetchフックのテストスイートを定義します
describe("useAuthFetch", () => {
	// 各テストの前にモックをリセットします
	beforeEach(() => {
		vi.clearAllMocks();
	});

	// 認証済みの場合のテストケース
	it("認証済みの場合、Authorizationヘッダー付きのfetch関数を返すこと", async () => {
		// モックのIDトークンを設定します
		const mockIdToken = "mock-id-token";
		// useAuthフックが返す値をモック化します
		(useAuth as Mock).mockReturnValue({ idToken: mockIdToken });

		// useAuthFetchフックをレンダリングし、結果を取得します
		const { result } = renderHook(() => useAuthFetch());

		// テスト用のURLとオプションを定義します
		const url = "https://api.example.com/data";
		const options = { method: "GET" };

		// フックが返す関数を非同期で実行します
		await act(async () => {
			await result.current(url, options);
		});

		// モック化されたfetch関数が正しく呼び出されたか検証します
		expect(mockFetch).toHaveBeenCalledWith(url, {
			...options,
			headers: {
				Authorization: `Bearer ${mockIdToken}`,
			},
		});
	});

	// 認証されていない場合のテストケース
	it("認証されていない場合、エラーをスローすること", async () => {
		// useAuthフックが認証されていない状態を返すようモック化します
		(useAuth as Mock).mockReturnValue({ idToken: null });

		// useAuthFetchフックをレンダリングします
		const { result } = renderHook(() => useAuthFetch());

		// テスト用のURLを定義します
		const url = "https://api.example.com/data";

		// フックが返す関数を実行し、エラーがスローされることを確認します
		await expect(
			act(async () => {
				await result.current(url);
			}),
		).rejects.toThrow("認証されていません");
	});

	// 既存のヘッダーがある場合のテストケース
	it("既存のヘッダーを保持しつつ、Authorizationヘッダーを追加すること", async () => {
		// モックのIDトークンを設定します
		const mockIdToken = "mock-id-token";
		// useAuthフックが返す値をモック化します
		(useAuth as Mock).mockReturnValue({ idToken: mockIdToken });

		// useAuthFetchフックをレンダリングします
		const { result } = renderHook(() => useAuthFetch());

		// テスト用のURLと既存のヘッダーを含むオプションを定義します
		const url = "https://api.example.com/data";
		const options = {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
		};

		// フックが返す関数を非同期で実行します
		await act(async () => {
			await result.current(url, options);
		});

		// モック化されたfetch関数が正しく呼び出されたか検証します
		// 既存のヘッダーが保持され、かつAuthorizationヘッダーが追加されていることを確認します
		expect(mockFetch).toHaveBeenCalledWith(url, {
			...options,
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${mockIdToken}`,
			},
		});
	});
});
