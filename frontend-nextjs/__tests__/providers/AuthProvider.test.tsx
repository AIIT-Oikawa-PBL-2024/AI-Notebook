import { getFirebaseAuth } from "@/lib/firebase";
import { AuthProvider, useAuth } from "@/providers/AuthProvider";
import { act, render, renderHook, waitFor } from "@testing-library/react";
import * as firebaseAuth from "firebase/auth";
import type { User } from "firebase/auth";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// Firebase Auth のモック
vi.mock("@/lib/firebase", () => ({
	getFirebaseAuth: vi.fn(),
}));

vi.mock("firebase/auth", async () => {
	const actual = await vi.importActual("firebase/auth");
	return {
		...actual,
		browserLocalPersistence: "LOCAL",
		setPersistence: vi.fn(),
		signOut: vi.fn(),
		onAuthStateChanged: vi.fn((auth, callback) => {
			(callback as (user: User | null) => void)(null);
			return () => {};
		}),
		onIdTokenChanged: vi.fn((auth, callback) => {
			(callback as (user: User | null) => void)(null);
			return () => {};
		}),
	};
});

describe("AuthProvider", () => {
	const mockAuth = {
		currentUser: null,
	};

	const mockUser = {
		email: "test@example.com",
		getIdToken: vi.fn().mockResolvedValue("mock-id-token"),
	};

	beforeEach(() => {
		vi.clearAllMocks();
		(getFirebaseAuth as Mock).mockReturnValue(mockAuth);
		vi.mocked(firebaseAuth.setPersistence).mockResolvedValue();

		vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(null);
				return () => {};
			},
		);

		vi.mocked(firebaseAuth.onIdTokenChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(null);
				return () => {};
			},
		);
	});

	it("初期状態では user と idToken が null であること", async () => {
		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.user).toBeNull();
			expect(result.current.idToken).toBeNull();
			expect(result.current.error).toBeNull();
		});
	});

	it("ユーザーがサインインした時、user と idToken が設定されること", async () => {
		vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(mockUser as unknown as User);
				return () => {};
			},
		);

		vi.mocked(firebaseAuth.onIdTokenChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(mockUser as unknown as User);
				return () => {};
			},
		);

		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.user).toEqual(mockUser);
			expect(result.current.idToken).toBe("mock-id-token");
		});
	});

	it("認証エラーが発生した時、error が設定されること", async () => {
		const mockError = new Error("認証エラー");
		vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation(() => {
			throw mockError;
		});

		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.error).toBe("認証の初期化に失敗しました。");
		});
	});

	it("認証トークンの取得に失敗した時、error が設定されること", async () => {
		const mockError = new Error("認証トークンの取得に失敗");
		const mockTokenErrorUser = {
			...mockUser,
			getIdToken: vi.fn().mockRejectedValue(mockError),
		};

		vi.mocked(firebaseAuth.onIdTokenChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(
					mockTokenErrorUser as unknown as User,
				);
				return () => {};
			},
		);

		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.error).toBe(
				"認証トークンの更新に失敗しました。再度サインインしてください。",
			);
		});
	});

	// 永続化に関する新しいテストケース
	it("初期化時に永続化が LOCAL に設定されること", async () => {
		renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(firebaseAuth.setPersistence).toHaveBeenCalledWith(
				mockAuth,
				firebaseAuth.browserLocalPersistence,
			);
		});
	});

	it("永続化の設定に失敗した時、error が設定されること", async () => {
		const mockError = new Error("永続化の設定に失敗");
		vi.mocked(firebaseAuth.setPersistence).mockRejectedValueOnce(mockError);

		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.error).toBe("認証の初期化に失敗しました。");
		});
	});

	it("永続化されたユーザーが存在する場合、currentUser から認証状態が復元されること", async () => {
		// モックのcurrentUserを設定
		const mockAuthWithUser = {
			currentUser: mockUser,
		};
		(getFirebaseAuth as Mock).mockReturnValue(mockAuthWithUser);

		// Auth State Changedのモックを更新
		vi.mocked(firebaseAuth.onAuthStateChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(mockUser as unknown as User);
				return () => {};
			},
		);

		// ID Token Changedのモックを更新
		vi.mocked(firebaseAuth.onIdTokenChanged).mockImplementation(
			(auth, callback) => {
				(callback as (user: User | null) => void)(mockUser as unknown as User);
				return () => {};
			},
		);

		const { result } = renderHook(() => useAuth(), {
			wrapper: AuthProvider,
		});

		await waitFor(() => {
			expect(result.current.user).toEqual(mockUser);
			expect(result.current.idToken).toBe("mock-id-token");
		});
	});
});
