import UploadPage from "@/app/(dashboard)/page";
import { useSignOut } from "@/hooks/useSignOut";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen } from "@testing-library/react";
import { type Mock, describe, expect, it, vi } from "vitest";

vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

vi.mock("@/hooks/useSignOut", () => ({
	useSignOut: vi.fn(),
}));

vi.mock("@/utils/withAuth", () => ({
	withAuth: (component: React.ComponentType) => component,
}));

vi.mock("@/features/(dashboard)/FileUpload", () => ({
	__esModule: true,
	default: () => <div>FileUpload Component</div>,
}));

describe("UploadPage", () => {
	it("ユーザーがいる場合に正しくレンダリングされること", () => {
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

		render(<UploadPage />);

		expect(screen.getByText("ファイルアップロード")).toBeInTheDocument();
		expect(screen.getByText("ユーザー: テストユーザー")).toBeInTheDocument();
		expect(screen.getByText("サインアウト")).toBeInTheDocument();
		expect(screen.getByText("FileUpload Component")).toBeInTheDocument();
	});

	it("サインアウトボタンがクリックされたときにsignOutUserが呼び出されること", () => {
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

		render(<UploadPage />);

		const signOutButton = screen.getByText("サインアウト");
		fireEvent.click(signOutButton);

		expect(signOutUserMock).toHaveBeenCalled();
	});

	it("isLoadingがtrueのときにサインアウトボタンが無効化されること", () => {
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

		render(<UploadPage />);

		const signOutButton = screen.getByText("サインアウト中...");
		expect(signOutButton).toBeDisabled();
	});

	it("エラーが存在する場合にエラーメッセージが表示されること", () => {
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

		render(<UploadPage />);

		expect(screen.getByText("エラーが発生しました")).toBeInTheDocument();
	});
});
