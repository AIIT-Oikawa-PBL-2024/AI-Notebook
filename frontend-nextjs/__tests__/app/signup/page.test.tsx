import SignUpPage from "@/app/(auth)/signup/page";
import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";

// BackgroundCardとSignUpFormをモック
vi.mock("@/components/layouts/BackgroundCard", () => ({
	BackgroundCard: () => (
		<div data-testid="background-card">Mocked BackgroundCard</div>
	),
}));

vi.mock("@/features/signup/SignUpForm", () => ({
	SignUpForm: () => <div data-testid="sign-up-form">Mocked SignUpForm</div>,
}));

describe("SignUpPage", () => {
	it("正しい構造でレンダリングされる", () => {
		render(<SignUpPage />);

		// メインコンテナのチェック
		const mainElement = screen.getByRole("main");
		expect(mainElement).toBeInTheDocument();
		expect(mainElement).toHaveClass(
			"flex min-h-screen justify-center items-center bg-gray-100 p-4",
		);

		// 内部のコンテナのチェック
		const innerContainer = mainElement.firstChild as HTMLElement;
		expect(innerContainer).toHaveClass("flex bg-gray max-w-5xl w-full");

		// BackgroundCardのチェック
		const backgroundCardContainer =
			screen.getByTestId("background-card").parentElement;
		expect(backgroundCardContainer).toHaveClass(
			"hidden md:flex md:w-1/2 p-6 items-center",
		);

		// SignUpFormのチェック
		const signUpFormContainer =
			screen.getByTestId("sign-up-form").parentElement;
		expect(signUpFormContainer).toHaveClass(
			"w-full md:w-1/2 p-6 flex items-center",
		);
	});

	it("BackgroundCardとSignUpFormが存在する", () => {
		render(<SignUpPage />);
		expect(screen.getByTestId("background-card")).toBeInTheDocument();
		expect(screen.getByTestId("sign-up-form")).toBeInTheDocument();
	});

	it("BackgroundCardが適切なレスポンシブクラスを持つ", () => {
		render(<SignUpPage />);
		const backgroundCardContainer =
			screen.getByTestId("background-card").parentElement;
		expect(backgroundCardContainer).toHaveClass("hidden md:flex");
	});

	it("SignUpFormが適切なレスポンシブクラスを持つ", () => {
		render(<SignUpPage />);
		const signUpFormContainer =
			screen.getByTestId("sign-up-form").parentElement;
		expect(signUpFormContainer).toHaveClass("w-full md:w-1/2");
	});
});
