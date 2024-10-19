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

	beforeEach(() => {
		vi.clearAllMocks();
		(useRouter as Mock).mockReturnValue({ push: mockPush });
	});

	it("should sign out successfully", async () => {
		(signOut as Mock).mockResolvedValue(undefined);

		const { result } = renderHook(() => useSignOut());

		expect(result.current.isLoading).toBe(false);
		expect(result.current.error).toBeNull();

		await act(async () => {
			await result.current.signOutUser();
		});

		expect(signOut).toHaveBeenCalled();
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
});
