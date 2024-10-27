import NavBar from "@/components/layouts/NavBar";
import { useSignOut } from "@/hooks/useSignOut";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// 必要なフックをモックします
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

vi.mock("@/hooks/useSignOut", () => ({
	useSignOut: vi.fn(),
}));

describe("NavBar", () => {
	beforeEach(() => {
		// 各テストごとにモックをクリアします
		vi.clearAllMocks();
	});

	it("NavBarコンポーネントがレンダリングされること", () => {
		(useAuth as Mock).mockReturnValue({
			user: {
				displayName: "テストユーザー",
				email: "test@example.com",
			},
		});
		(useSignOut as Mock).mockReturnValue({
			signOutUser: vi.fn(),
			error: null,
			isLoading: false,
		});

		render(<NavBar />);
		expect(screen.getByText("AIノートブック")).toBeInTheDocument();
	});

	it("ログインしていない場合、ユーザー情報とサインアウトボタンが表示されないこと", () => {
		(useAuth as Mock).mockReturnValue({ user: null });
		(useSignOut as Mock).mockReturnValue({
			signOutUser: vi.fn(),
			error: null,
			isLoading: false,
		});

		render(<NavBar />);
		expect(screen.queryByText(/ユーザー:/)).not.toBeInTheDocument();
		expect(screen.queryByText("サインアウト")).not.toBeInTheDocument();
	});

	it("ログインしている場合、ユーザー情報とサインアウトボタンが表示されること", () => {
		(useAuth as Mock).mockReturnValue({
			user: {
				displayName: "テストユーザー",
				email: "test@example.com",
			},
		});
		(useSignOut as Mock).mockReturnValue({
			signOutUser: vi.fn(),
			error: null,
			isLoading: false,
		});

		render(<NavBar />);
		expect(screen.getByText("ユーザー: テストユーザー")).toBeInTheDocument();
		expect(screen.getByText("サインアウト")).toBeInTheDocument();
	});

	it("サインアウトボタンをクリックすると、signOutUserが呼び出されること", () => {
		const signOutUserMock = vi.fn();
		(useAuth as Mock).mockReturnValue({
			user: {
				displayName: "テストユーザー",
				email: "test@example.com",
			},
		});
		(useSignOut as Mock).mockReturnValue({
			signOutUser: signOutUserMock,
			error: null,
			isLoading: false,
		});

		render(<NavBar />);

		const signOutButton = screen.getByText("サインアウト");
		fireEvent.click(signOutButton);

		expect(signOutUserMock).toHaveBeenCalled();
	});

	it("isLoadingがtrueの場合、サインアウトボタンが無効化されること", () => {
		(useAuth as Mock).mockReturnValue({
			user: {
				displayName: "テストユーザー",
				email: "test@example.com",
			},
		});
		(useSignOut as Mock).mockReturnValue({
			signOutUser: vi.fn(),
			error: null,
			isLoading: true,
		});

		render(<NavBar />);

		const signOutButton = screen.getByText("サインアウト中...");
		expect(signOutButton).toBeDisabled();
	});

	it("エラーが存在する場合、エラーメッセージが表示されること", () => {
		(useAuth as Mock).mockReturnValue({
			user: {
				displayName: "テストユーザー",
				email: "test@example.com",
			},
		});
		(useSignOut as Mock).mockReturnValue({
			signOutUser: vi.fn(),
			error: "エラーが発生しました",
			isLoading: false,
		});

		render(<NavBar />);

		expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
	});

	// 既存のメニュー項目のテスト
	it("ホームメニュー項目が表示されること", () => {
		render(<NavBar />);
		expect(screen.getByText("ホーム")).toBeInTheDocument();
	});

	it("ファイル選択メニュー項目が表示されること", () => {
		render(<NavBar />);
		expect(screen.getByText("ファイル選択")).toBeInTheDocument();
	});

	it("AI出力メニュー項目が表示されること", () => {
		render(<NavBar />);
		expect(screen.getByText("AI出力")).toBeInTheDocument();
	});

	it("AI練習問題メニュー項目が表示されること", () => {
		render(<NavBar />);
		expect(screen.getByText("AI練習問題")).toBeInTheDocument();
	});

	it("ノートメニュー項目が表示されること", () => {
		render(<NavBar />);
		expect(screen.getByText("ノート")).toBeInTheDocument();
	});
});
