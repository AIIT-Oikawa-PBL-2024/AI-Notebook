// AuthProvider.test.tsx

import { AuthProvider, useAuth } from "@/providers/AuthProvider";
import { act, render, screen, waitFor } from "@testing-library/react";
import {
	type User,
	getAuth,
	onAuthStateChanged,
	onIdTokenChanged,
	signOut,
} from "firebase/auth";
import React from "react";
import { type Mock, afterEach, describe, expect, it, vi } from "vitest";

// Firebaseの関数をモック化
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(),
	onAuthStateChanged: vi.fn(),
	onIdTokenChanged: vi.fn(),
	signOut: vi.fn(),
}));

vi.mock("@/lib/firebase", () => ({
	initFirebase: vi.fn(),
}));

describe("AuthProvider", () => {
	afterEach(() => {
		vi.clearAllMocks();
	});

	const mockUser: User = {
		uid: "user123",
		getIdToken: vi.fn().mockResolvedValue("mock-id-token"),
		emailVerified: false,
		isAnonymous: false,
		providerData: [],
		refreshToken: "",
		tenantId: null,
		delete: vi.fn(),
		reload: vi.fn(),
		getIdTokenResult: vi.fn(),
		toJSON: vi.fn(),
		email: null,
		displayName: null,
		phoneNumber: null,
		photoURL: null,
		providerId: "firebase",
		metadata: {
			creationTime: "",
			lastSignInTime: "",
		},
	};

	const ConsumerComponent = () => {
		const { user, idToken, error, reAuthenticate, clearError } = useAuth();
		return (
			<div>
				<span data-testid="user-uid">{user?.uid || "no-user"}</span>
				<span data-testid="id-token">{idToken || "no-token"}</span>
				<span data-testid="error">{error || "no-error"}</span>
				<button
					type="button"
					onClick={reAuthenticate}
					data-testid="re-auth-button"
				>
					Re-authenticate
				</button>
				<button
					type="button"
					onClick={clearError}
					data-testid="clear-error-button"
				>
					Clear Error
				</button>
			</div>
		);
	};

	it("認証されている場合、ユーザーとidTokenを提供する", async () => {
		const mockAuth = {};
		(getAuth as Mock).mockReturnValue(mockAuth);
		(onAuthStateChanged as Mock).mockImplementation((auth, callback) => {
			callback(mockUser);
			return () => {};
		});
		(onIdTokenChanged as Mock).mockImplementation((auth, callback) => {
			callback(mockUser);
			return () => {};
		});

		render(
			<AuthProvider>
				<ConsumerComponent />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("user-uid").textContent).toBe("user123");
			expect(screen.getByTestId("id-token").textContent).toBe("mock-id-token");
		});
	});

	it("認証されていない場合、ユーザーとidTokenはnullである", async () => {
		const mockAuth = {};
		(getAuth as Mock).mockReturnValue(mockAuth);
		(onAuthStateChanged as Mock).mockImplementation((auth, callback) => {
			callback(null);
			return () => {};
		});
		(onIdTokenChanged as Mock).mockImplementation((auth, callback) => {
			callback(null);
			return () => {};
		});

		render(
			<AuthProvider>
				<ConsumerComponent />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("user-uid").textContent).toBe("no-user");
			expect(screen.getByTestId("id-token").textContent).toBe("no-token");
		});
	});

	it("ユーザーのサインアウトを正しく処理する", async () => {
		const mockAuth = {};
		(getAuth as Mock).mockReturnValue(mockAuth);

		let authCallback: (user: User | null) => void = () => {};
		let idTokenCallback: (user: User | null) => void = () => {};

		(onAuthStateChanged as Mock).mockImplementation((auth, callback) => {
			authCallback = callback;
			return () => {};
		});

		(onIdTokenChanged as Mock).mockImplementation((auth, callback) => {
			idTokenCallback = callback;
			return () => {};
		});

		render(
			<AuthProvider>
				<ConsumerComponent />
			</AuthProvider>,
		);

		// ユーザーのサインインをシミュレート
		act(() => {
			authCallback(mockUser);
			idTokenCallback(mockUser);
		});

		await waitFor(() => {
			expect(screen.getByTestId("user-uid").textContent).toBe("user123");
			expect(screen.getByTestId("id-token").textContent).toBe("mock-id-token");
		});

		// ユーザーのサインアウトをシミュレート
		act(() => {
			authCallback(null);
			idTokenCallback(null);
		});

		await waitFor(() => {
			expect(screen.getByTestId("user-uid").textContent).toBe("no-user");
			expect(screen.getByTestId("id-token").textContent).toBe("no-token");
		});
	});

	it("トークン更新エラーを処理し、再認証を促す", async () => {
		const mockAuth = {};
		(getAuth as Mock).mockReturnValue(mockAuth);

		let idTokenCallback: (user: User | null) => void = () => {};

		(onAuthStateChanged as Mock).mockImplementation((auth, callback) => {
			callback(mockUser);
			return () => {};
		});

		(onIdTokenChanged as Mock).mockImplementation((auth, callback) => {
			idTokenCallback = callback;
			return () => {};
		});

		(signOut as Mock).mockResolvedValue(undefined);

		render(
			<AuthProvider>
				<ConsumerComponent />
			</AuthProvider>,
		);

		// トークン更新エラーをシミュレート
		act(() => {
			idTokenCallback({
				...mockUser,
				getIdToken: vi
					.fn()
					.mockRejectedValue(new Error("Token refresh failed")),
			});
		});

		await waitFor(() => {
			expect(screen.getByTestId("error").textContent).toBe(
				"認証トークンの更新に失敗しました。再度サインインしてください",
			);
		});

		// 再認証ボタンをクリック
		act(() => {
			screen.getByTestId("re-auth-button").click();
		});

		await waitFor(() => {
			expect(screen.getByTestId("error").textContent).toBe(
				"認証トークンの更新に失敗しました。再度サインインしてください",
			);
			expect(signOut).toHaveBeenCalled();
		});
	});

	it("エラーをクリアする", async () => {
		const mockAuth = {};
		(getAuth as Mock).mockReturnValue(mockAuth);

		(onAuthStateChanged as Mock).mockImplementation((auth, callback) => {
			callback(mockUser);
			return () => {};
		});

		(onIdTokenChanged as Mock).mockImplementation((auth, callback) => {
			callback({
				...mockUser,
				getIdToken: vi
					.fn()
					.mockRejectedValue(new Error("Token refresh failed")),
			});
			return () => {};
		});

		render(
			<AuthProvider>
				<ConsumerComponent />
			</AuthProvider>,
		);

		await waitFor(() => {
			expect(screen.getByTestId("error").textContent).toBe(
				"認証トークンの更新に失敗しました。再度サインインしてください",
			);
		});

		// エラークリアボタンをクリック
		act(() => {
			screen.getByTestId("clear-error-button").click();
		});

		await waitFor(() => {
			expect(screen.getByTestId("error").textContent).toBe("no-error");
		});
	});
});
