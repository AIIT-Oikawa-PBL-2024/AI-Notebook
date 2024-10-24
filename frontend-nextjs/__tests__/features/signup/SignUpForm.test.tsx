import { SignUpForm } from "@/features/signup/SignUpForm";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import {
	createUserWithEmailAndPassword,
	getAuth,
	sendEmailVerification,
	signInWithPopup,
} from "firebase/auth";
import { useRouter } from "next/navigation";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// Firebaseのモック
vi.mock("firebase/app", () => ({
	initializeApp: vi.fn(),
}));

// firebase/authのモック
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(() => ({})),
	createUserWithEmailAndPassword: vi.fn(),
	sendEmailVerification: vi.fn(),
	signInWithPopup: vi.fn(),
	GoogleAuthProvider: vi.fn(),
}));

// next/navigationのモック
vi.mock("next/navigation", () => ({
	useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

// AuthProviderのモック
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(() => ({ setUser: vi.fn() })),
}));

describe("SignUpForm", () => {
	let mockSetUser: Mock;
	let mockPush: Mock;

	beforeEach(() => {
		vi.clearAllMocks();

		mockSetUser = vi.fn();
		(useAuth as Mock).mockReturnValue({ setUser: mockSetUser });

		mockPush = vi.fn();
		(useRouter as Mock).mockReturnValue({ push: mockPush });
	});

	it("フォームが正しくレンダリングされる", () => {
		render(<SignUpForm />);
		expect(
			screen.getByRole("heading", { name: "Sign Up" }),
		).toBeInTheDocument();
		expect(screen.getByRole("button", { name: "Sign Up" })).toBeInTheDocument();
		expect(screen.getByPlaceholderText("name@mail.com")).toBeInTheDocument();
		expect(screen.getByPlaceholderText("********")).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: "Sign in with Google" }),
		).toBeInTheDocument();
	});

	it("メールアドレスとパスワードの入力値が更新される", () => {
		render(<SignUpForm />);
		const emailInput = screen.getByPlaceholderText("name@mail.com");
		const passwordInput = screen.getByPlaceholderText("********");

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "Password123!" } });

		expect(emailInput).toHaveValue("test@example.com");
		expect(passwordInput).toHaveValue("Password123!");
	});

	it("無効なメールアドレスでエラーメッセージが表示される", async () => {
		render(<SignUpForm />);
		const emailInput = screen.getByPlaceholderText("name@mail.com");

		fireEvent.change(emailInput, { target: { value: "invalid-email" } });
		fireEvent.blur(emailInput);

		await waitFor(() => {
			expect(
				screen.getByText("有効なメールアドレスを入力してください。"),
			).toBeInTheDocument();
		});
	});

	it("パスワードバリデーションが正しく機能する", async () => {
		render(<SignUpForm />);
		const passwordInput = screen.getByPlaceholderText("********");

		// 弱いパスワード
		fireEvent.change(passwordInput, { target: { value: "weak" } });
		await waitFor(() => {
			expect(screen.getByText("8文字以上")).toHaveClass("text-red-700");
			expect(screen.getByText("大文字を含む")).toHaveClass("text-red-700");
			expect(screen.getByText("小文字を含む")).toHaveClass("text-green-700");
			expect(screen.getByText("数字を含む")).toHaveClass("text-red-700");
			expect(screen.getByText("特殊文字を含む")).toHaveClass("text-red-700");
			expect(screen.getByText("スペースを含まない")).toHaveClass(
				"text-green-700",
			);
		});

		// 強いパスワード
		fireEvent.change(passwordInput, { target: { value: "StrongP@ssw0rd" } });
		await waitFor(() => {
			expect(screen.getByText("8文字以上")).toHaveClass("text-green-700");
			expect(screen.getByText("大文字を含む")).toHaveClass("text-green-700");
			expect(screen.getByText("小文字を含む")).toHaveClass("text-green-700");
			expect(screen.getByText("数字を含む")).toHaveClass("text-green-700");
			expect(screen.getByText("特殊文字を含む")).toHaveClass("text-green-700");
			expect(screen.getByText("スペースを含まない")).toHaveClass(
				"text-green-700",
			);
		});
	});

	it("メールサインアップが成功した場合、確認メール送信画面が表示される", async () => {
		const mockAuth = getAuth();
		(createUserWithEmailAndPassword as Mock).mockResolvedValueOnce({
			user: {},
		});
		(sendEmailVerification as Mock).mockResolvedValueOnce(undefined);

		render(<SignUpForm />);
		const emailInput = screen.getByPlaceholderText("name@mail.com");
		const passwordInput = screen.getByPlaceholderText("********");
		const signUpButton = screen.getByRole("button", { name: "Sign Up" });

		fireEvent.change(emailInput, { target: { value: "test@example.com" } });
		fireEvent.change(passwordInput, { target: { value: "StrongP@ssw0rd" } });
		fireEvent.click(signUpButton);

		await waitFor(() => {
			expect(screen.getByText("Email Verification Sent")).toBeInTheDocument();
		});
	});

	it("Googleサインインが成功した場合、ユーザーを設定しホームにリダイレクトする", async () => {
		const mockUser = { email: "test@example.com" };
		(signInWithPopup as Mock).mockResolvedValueOnce({ user: mockUser });

		render(<SignUpForm />);
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

		render(<SignUpForm />);
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

	it("サインインページへのリンクがある", () => {
		render(<SignUpForm />);
		const signInLink = screen.getByText("サインインへ");
		expect(signInLink).toHaveAttribute("href", "/signin");
	});
});
