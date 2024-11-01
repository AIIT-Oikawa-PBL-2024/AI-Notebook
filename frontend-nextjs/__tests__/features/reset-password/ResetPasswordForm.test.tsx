import ResetPasswordForm from "@/features/auth/reset-password/ResetPasswordForm";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { getAuth, sendPasswordResetEmail } from "firebase/auth";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// Firebaseのモック
vi.mock("firebase/app", () => ({
	initializeApp: vi.fn(),
}));

// firebase/authのモック
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(() => ({})),
	sendPasswordResetEmail: vi.fn(),
}));

describe("ResetPasswordForm", () => {
	// 各テスト前にモックをクリア
	beforeEach(() => {
		vi.clearAllMocks();
	});

	// フォームが正しくレンダリングされるかテスト
	it("フォームが正しくレンダリングされる", () => {
		render(<ResetPasswordForm />);
		expect(screen.getByText("Password Reset")).toBeInTheDocument();
		expect(screen.getByLabelText("Email")).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Reset Password" }),
		).toBeInTheDocument();
	});

	// メールアドレス入力時の状態更新をテスト
	it("メールアドレス入力時に状態が更新される", () => {
		render(<ResetPasswordForm />);
		const emailInput = screen.getByLabelText("Email");
		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		expect(emailInput).toHaveValue("test@example.com");
	});

	// パスワードリセット成功時のメッセージ表示をテスト
	it("パスワードリセット成功時にメッセージが表示される", async () => {
		const mockAuth = getAuth();
		(sendPasswordResetEmail as Mock).mockResolvedValueOnce(undefined);

		render(<ResetPasswordForm />);
		const emailInput = screen.getByLabelText("Email");
		const submitButton = screen.getByRole("button", { name: "Reset Password" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.click(submitButton);

		// 成功メッセージが表示されるまで待機
		await waitFor(() => {
			expect(
				screen.getByText(
					"パスワードリセット用のメールを送信しました。メールをご確認ください。",
				),
			).toBeInTheDocument();
		});

		// sendPasswordResetEmailが正しい引数で呼び出されたか確認
		expect(sendPasswordResetEmail).toHaveBeenCalledWith(
			mockAuth,
			"test@example.com",
		);
	});

	// パスワードリセット失敗時のエラーメッセージ表示をテスト
	it("パスワードリセット失敗時にエラーメッセージが表示される", async () => {
		const mockAuth = getAuth();
		(sendPasswordResetEmail as Mock).mockRejectedValueOnce(
			new Error("Reset failed"),
		);

		render(<ResetPasswordForm />);
		const emailInput = screen.getByLabelText("Email");
		const submitButton = screen.getByRole("button", { name: "Reset Password" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.click(submitButton);

		// エラーメッセージが表示されるまで待機
		await waitFor(() => {
			expect(
				screen.getByText(
					"パスワードリセットに失敗しました。メールアドレスを確認してください。",
				),
			).toBeInTheDocument();
		});

		// sendPasswordResetEmailが正しい引数で呼び出されたか確認
		expect(sendPasswordResetEmail).toHaveBeenCalledWith(
			mockAuth,
			"test@example.com",
		);
	});

	// サインインページへのリンクが存在するかテスト
	it("サインインページへのリンクが存在する", () => {
		render(<ResetPasswordForm />);
		const signInLink = screen.getByText("サインインページに戻る");
		expect(signInLink).toHaveAttribute("href", "/signin");
	});
});
