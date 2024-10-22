import { useSignOut } from "@/hooks/useSignOut";
import { act, renderHook } from "@testing-library/react";
import { signOut } from "firebase/auth";
import { useRouter } from "next/navigation";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モックの設定
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(),
	signOut: vi.fn(),
}));

vi.mock("next/navigation", () => ({
	useRouter: vi.fn(),
}));

describe("useSignOut", () => {
	const mockPush = vi.fn();
	const mockClear = vi.fn();
	const mockCacheDelete = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		(useRouter as Mock).mockReturnValue({ push: mockPush });

		// ローカルストレージとセッションストレージのモック
		Object.defineProperty(window, "localStorage", {
			value: { clear: mockClear },
			writable: true,
		});
		Object.defineProperty(window, "sessionStorage", {
			value: { clear: mockClear },
			writable: true,
		});

		// クッキーのモック
		let cookies: string[] = ["test=value"];
		Object.defineProperty(document, "cookie", {
			get: () => cookies.join("; "),
			set: (value) => {
				const [name, ...rest] = value.split("=");
				const newCookie = `${name}=${rest.join("=")}`;
				const index = cookies.findIndex((c) => c.startsWith(`${name}=`));
				if (index !== -1) {
					cookies[index] = newCookie;
				} else {
					cookies.push(newCookie);
				}
				if (newCookie.includes("expires=Thu, 01 Jan 1970 00:00:00 GMT")) {
					cookies = cookies.filter((c) => !c.startsWith(`${name}=`));
				}
			},
			configurable: true,
		});

		// キャッシュのモック
		Object.defineProperty(window, "caches", {
			value: {
				keys: vi.fn().mockResolvedValue(["test-cache"]),
				delete: mockCacheDelete,
			},
			writable: true,
		});
	});

	it("should sign out successfully and clear data", async () => {
		(signOut as Mock).mockResolvedValue(undefined);

		const { result } = renderHook(() => useSignOut());

		await act(async () => {
			await result.current.signOutUser();
		});

		expect(signOut).toHaveBeenCalled();
		expect(mockClear).toHaveBeenCalledTimes(2); // localStorage と sessionStorage
		expect(document.cookie).toBe("");
		expect(mockCacheDelete).toHaveBeenCalledWith("test-cache");
		expect(mockPush).toHaveBeenCalledWith("/signin");
		expect(result.current.isLoading).toBe(false);
		expect(result.current.error).toBeNull();
	});

	it("should handle sign out error", async () => {
		const errorMessage = "サインアウト中にエラーが発生しました。";
		(signOut as Mock).mockRejectedValue(new Error("Sign out failed"));

		const { result } = renderHook(() => useSignOut());

		await act(async () => {
			await result.current.signOutUser();
		});

		expect(signOut).toHaveBeenCalled();
		expect(mockPush).not.toHaveBeenCalled();
		expect(result.current.isLoading).toBe(false);
		expect(result.current.error).toBe(errorMessage);
	});

	it("should set loading state during sign out process", async () => {
		let resolveSignOut: () => void;
		const signOutPromise = new Promise<void>((resolve) => {
			resolveSignOut = resolve;
		});
		(signOut as Mock).mockReturnValue(signOutPromise);

		const { result } = renderHook(() => useSignOut());

		let signOutUserPromise: Promise<void>;
		act(() => {
			signOutUserPromise = result.current.signOutUser();
		});

		// Wait for next tick to allow state updates
		await act(async () => {
			await new Promise((resolve) => setTimeout(resolve, 0));
		});

		expect(result.current.isLoading).toBe(true);

		act(() => {
			resolveSignOut();
		});

		await act(async () => {
			await signOutUserPromise;
		});

		expect(result.current.isLoading).toBe(false);
	});

	it("should handle cache clearing error", async () => {
		(signOut as Mock).mockResolvedValue(undefined);
		(window.caches.delete as Mock).mockRejectedValue(
			new Error("Cache delete failed"),
		);

		const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

		const { result } = renderHook(() => useSignOut());

		await act(async () => {
			await result.current.signOutUser();
		});

		expect(consoleSpy).toHaveBeenCalledWith(
			"キャッシュのクリアに失敗しました:",
			expect.any(Error),
		);
		expect(mockPush).toHaveBeenCalledWith("/signin");
		expect(result.current.isLoading).toBe(false);
		expect(result.current.error).toBeNull();

		consoleSpy.mockRestore();
	});
});
