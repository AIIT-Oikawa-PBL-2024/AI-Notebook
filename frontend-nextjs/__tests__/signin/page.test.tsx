import SignInPage from "@/app/signin/page";
import { render, screen } from "@testing-library/react";
import React from "react";
import { describe, expect, it, vi } from "vitest";

// BackgroundCardとSignInFormをモック
vi.mock("@/app/components/BackgroundCard", () => ({
	BackgroundCard: () => (
		<div data-testid="background-card">Mocked BackgroundCard</div>
	),
}));

vi.mock("@/app/components/signin/SignInForm", () => ({
	SignInForm: () => <div data-testid="sign-in-form">Mocked SignInForm</div>,
}));

describe("SignInPage", () => {
	it("正しい構造でレンダリングされる", () => {
		render(<SignInPage />);

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

		// SignInFormのチェック
		const signInFormContainer =
			screen.getByTestId("sign-in-form").parentElement;
		expect(signInFormContainer).toHaveClass(
			"w-full md:w-1/2 p-6 flex items-center",
		);
	});

	it("BackgroundCardとSignInFormが存在する", () => {
		render(<SignInPage />);
		expect(screen.getByTestId("background-card")).toBeInTheDocument();
		expect(screen.getByTestId("sign-in-form")).toBeInTheDocument();
	});

	it("BackgroundCardが適切なレスポンシブクラスを持つ", () => {
		render(<SignInPage />);
		const backgroundCardContainer =
			screen.getByTestId("background-card").parentElement;
		expect(backgroundCardContainer).toHaveClass("hidden md:flex");
	});

	it("SignInFormが適切なレスポンシブクラスを持つ", () => {
		render(<SignInPage />);
		const signInFormContainer =
			screen.getByTestId("sign-in-form").parentElement;
		expect(signInFormContainer).toHaveClass("w-full md:w-1/2");
	});
});
