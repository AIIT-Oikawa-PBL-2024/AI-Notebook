import ResetPasswordPage from "@/app/(auth)/reset-password/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// BackgroundCardとResetPasswordFormをモック
vi.mock("@/components/layouts/BackgroundCard", () => ({
	BackgroundCard: () => (
		<div data-testid="background-card">Mocked BackgroundCard</div>
	),
}));

vi.mock("@/features/reset-password/ResetPasswordForm", () => ({
	__esModule: true,
	default: () => (
		<div data-testid="reset-password-form">Mocked ResetPasswordForm</div>
	),
}));

describe("ResetPasswordPage", () => {
	it("メインコンテナをレンダリングする", () => {
		render(<ResetPasswordPage />);
		const mainElement = screen.getByRole("main");
		expect(mainElement).toBeInTheDocument();
		expect(mainElement).toHaveClass(
			"flex min-h-screen justify-center items-center bg-gray-100 p-4",
		);
	});

	it("大きな画面でBackgroundCardをレンダリングする", () => {
		render(<ResetPasswordPage />);
		const backgroundCard = screen.getByTestId("background-card");
		expect(backgroundCard).toBeInTheDocument();
		expect(backgroundCard.parentElement).toHaveClass(
			"hidden md:flex md:w-1/2 p-6 items-center",
		);
	});

	it("ResetPasswordFormをレンダリングする", () => {
		render(<ResetPasswordPage />);
		const resetPasswordForm = screen.getByTestId("reset-password-form");
		expect(resetPasswordForm).toBeInTheDocument();
		expect(resetPasswordForm.parentElement).toHaveClass(
			"w-full md:w-1/2 p-6 flex items-center",
		);
	});

	it("正しいレスポンシブレイアウトクラスを持っている", () => {
		render(<ResetPasswordPage />);
		const container = screen.getByRole("main").firstChild;
		expect(container).toHaveClass("flex bg-gray max-w-5xl w-full");
	});
});
