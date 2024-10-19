import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// ランダムなモックトークンを生成する関数
function generateMockToken(length = 32): string {
	const characters =
		"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
	let result = "";
	for (let i = 0; i < length; i++) {
		result += characters.charAt(Math.floor(Math.random() * characters.length));
	}
	return result;
}

vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

describe("useAuthFetch", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("認証済みの場合、Authorizationヘッダー付きのfetch関数を返すこと", async () => {
		const mockIdToken = generateMockToken();
		(useAuth as Mock).mockReturnValue({ idToken: mockIdToken });

		const { result } = renderHook(() => useAuthFetch());

		const url = "https://api.example.com/data";
		const options = { method: "GET" };

		await act(async () => {
			await result.current(url, options);
		});

		expect(mockFetch).toHaveBeenCalledWith(url, {
			...options,
			headers: {
				Authorization: `Bearer ${mockIdToken}`,
			},
		});
	});

	it("認証されていない場合、エラーをスローすること", async () => {
		(useAuth as Mock).mockReturnValue({ idToken: null });

		const { result } = renderHook(() => useAuthFetch());

		const url = "https://api.example.com/data";

		await expect(
			act(async () => {
				await result.current(url);
			}),
		).rejects.toThrow("認証されていません");
	});

	it("既存のヘッダーを保持しつつ、Authorizationヘッダーを追加すること", async () => {
		const mockIdToken = generateMockToken();
		(useAuth as Mock).mockReturnValue({ idToken: mockIdToken });

		const { result } = renderHook(() => useAuthFetch());

		const url = "https://api.example.com/data";
		const options = {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
		};

		await act(async () => {
			await result.current(url, options);
		});

		expect(mockFetch).toHaveBeenCalledWith(url, {
			...options,
			headers: {
				"Content-Type": "application/json",
				Authorization: `Bearer ${mockIdToken}`,
			},
		});
	});
});
