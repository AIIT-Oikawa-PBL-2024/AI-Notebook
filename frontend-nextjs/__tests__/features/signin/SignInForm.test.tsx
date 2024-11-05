import { SignInForm } from "@/features/auth/signin/SignInForm";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { signInWithEmailAndPassword, signInWithPopup } from "firebase/auth";
import { useRouter } from "next/navigation";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// FirebaseとNext.jsのモジュールをモック化
vi.mock("firebase/app", () => ({
	initializeApp: vi.fn(),
}));

vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(),
	signInWithEmailAndPassword: vi.fn(),
	signInWithPopup: vi.fn(),
	GoogleAuthProvider: vi.fn(),
}));

vi.mock("next/navigation", () => ({
	useRouter: vi.fn(),
}));

vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

describe("SignInForm", () => {
	let mockSetUser: Mock;
	let mockPush: Mock;

	beforeEach(() => {
		vi.clearAllMocks();

		mockSetUser = vi.fn();
		(useAuth as Mock).mockReturnValue({ setUser: mockSetUser });

		mockPush = vi.fn();
		(useRouter as Mock).mockReturnValue({ push: mockPush });
	});

	it("フォームを正しくレンダリングする", () => {
		render(<SignInForm />);
		expect(
			screen.getByRole("heading", { name: "Sign In" }),
		).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Sign In" })).toBeInTheDocument();
		expect(screen.getByLabelText("Email")).toBeInTheDocument();
		expect(screen.getByLabelText("Password")).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Sign in with Google" }),
		).toBeInTheDocument();
		expect(
			screen.getByText("パスワードを忘れた方はこちら"),
		).toBeInTheDocument();
		expect(screen.getByText("サインアップへ")).toBeInTheDocument();
	});

	it("メールとパスワードの入力値を更新する", () => {
		render(<SignInForm />);
		const emailInput = screen.getByLabelText("Email");
		const passwordInput = screen.getByLabelText("Password");

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "password123" } });

		expect(emailInput).toHaveValue("test@example.com");
		expect(passwordInput).toHaveValue("password123");
	});

	it("メールサインインが成功した場合、ユーザーを設定しホームにリダイレクトする", async () => {
		const mockUser = { emailVerified: true };
		(signInWithEmailAndPassword as Mock).mockResolvedValueOnce({
			user: mockUser,
		});

		render(<SignInForm />);
		const emailInput = screen.getByLabelText("Email");
		const passwordInput = screen.getByLabelText("Password");
		const signInButton = screen.getByRole("button", { name: "Sign In" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "password123" } });
		fireEvent.click(signInButton);

		await waitFor(() => {
			expect(mockSetUser).toHaveBeenCalledWith(mockUser);
			expect(mockPush).toHaveBeenCalledWith("/");
		});
	});

	it("メールが未確認の場合、エラーメッセージを表示する", async () => {
		const mockUser = { emailVerified: false };
		(signInWithEmailAndPassword as Mock).mockResolvedValueOnce({
			user: mockUser,
		});

		render(<SignInForm />);
		const emailInput = screen.getByLabelText("Email");
		const passwordInput = screen.getByLabelText("Password");
		const signInButton = screen.getByRole("button", { name: "Sign In" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "password123" } });
		fireEvent.click(signInButton);

		await waitFor(() => {
			expect(
				screen.getByText(
					"メールアドレスが確認されていません。メールを確認してアカウントを有効化してください。",
				),
			).toBeInTheDocument();
		});
	});

	it("メールサインインが失敗した場合、エラーメッセージを表示する", async () => {
		(signInWithEmailAndPassword as Mock).mockRejectedValueOnce(
			new Error("Sign-in failed"),
		);

		render(<SignInForm />);
		const emailInput = screen.getByLabelText("Email");
		const passwordInput = screen.getByLabelText("Password");
		const signInButton = screen.getByRole("button", { name: "Sign In" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "wrongpassword" } });
		fireEvent.click(signInButton);

		await waitFor(() => {
			expect(
				screen.getByText(
					"サインインに失敗しました。メールアドレスとパスワードを確認してください",
				),
			).toBeInTheDocument();
		});
	});

	it("Googleサインインが成功した場合、ユーザーを設定しホームにリダイレクトする", async () => {
		const mockUser = {};
		(signInWithPopup as Mock).mockResolvedValueOnce({ user: mockUser });

		render(<SignInForm />);
		const googleSignInButton = screen.getByRole("button", {
			name: "Sign in with Google",
		});

		fireEvent.click(googleSignInButton);

		await waitFor(() => {
			expect(mockSetUser).toHaveBeenCalledWith(mockUser);
			expect(mockPush).toHaveBeenCalledWith("/");
		});
	});

	it("Googleサインインが失敗した場合、エラーメッセージを表示する", async () => {
		(signInWithPopup as Mock).mockRejectedValueOnce(
			new Error("Google sign-in failed"),
		);

		render(<SignInForm />);
		const googleSignInButton = screen.getByRole("button", {
			name: "Sign in with Google",
		});

		fireEvent.click(googleSignInButton);

		await waitFor(() => {
			expect(
				screen.getByText(
					"サインインに失敗しました。Googleアカウントを確認してください",
				),
			).toBeInTheDocument();
		});
	});

	it("パスワードリセットページへのリンクがある", () => {
		render(<SignInForm />);
		const resetPasswordLink = screen.getByText("パスワードを忘れた方はこちら");
		expect(resetPasswordLink).toHaveAttribute("href", "/reset-password");
	});

	it("サインアップページへのリンクがある", () => {
		render(<SignInForm />);
		const signUpLink = screen.getByText("サインアップへ");
		expect(signUpLink).toHaveAttribute("href", "/signup");
	});

	it("入力フィールドが適切なautocomplete属性を持っている", () => {
		render(<SignInForm />);
		const emailInput = screen.getByLabelText("Email");
		const passwordInput = screen.getByLabelText("Password");	
		expect(emailInput).toHaveAttribute("autoComplete", "email");
		expect(passwordInput).toHaveAttribute("autoComplete", "current-password");
	});
});
