import RootLayout from "@/app/layout";
import { render } from "@testing-library/react";
import type React from "react";
import { describe, expect, it, vi } from "vitest";

// 必要なモジュールをモック
vi.mock("next/font/google", () => ({
	Inter: () => ({ variable: "mock-inter" }),
	Noto_Sans_JP: () => ({ variable: "mock-noto-sans-jp" }),
}));

vi.mock("@/providers/AuthProvider", () => ({
	AuthProvider: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="auth-provider">{children}</div>
	),
}));

vi.mock("@/providers/ClientThemeProvider", () => ({
	__esModule: true,
	default: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="client-theme-provider">{children}</div>
	),
}));

describe("RootLayout", () => {
	it("正しい言語属性でHTMLをレンダリングすること", () => {
		const { container } = render(
			<RootLayout>
				<div>Test Content</div>
			</RootLayout>,
		);
		const html = container.querySelector("html");
		expect(html).toHaveAttribute("lang", "ja");
	});

	it("正しいクラスと style をbody要素に適用すること", () => {
		const { container } = render(
			<RootLayout>
				<div>Test Content</div>
			</RootLayout>,
		);
		const body = container.querySelector("body");
		expect(body).toHaveClass(
			"mock-noto-sans-jp mock-inter font-sans antialiased",
		);
		expect(body).toHaveStyle({
			fontFamily:
				"var(--font-inter), var(--font-noto-sans-jp), Arial, 'Helvetica Neue', sans-serif",
		});
	});

	it("AuthProvider と ClientThemeProvider をレンダリングすること", () => {
		const { getByTestId } = render(
			<RootLayout>
				<div>Test Content</div>
			</RootLayout>,
		);
		expect(getByTestId("auth-provider")).toBeInTheDocument();
		expect(getByTestId("client-theme-provider")).toBeInTheDocument();
	});

	it("子要素を正しくレンダリングすること", () => {
		const { getByText } = render(
			<RootLayout>
				<div>Test Content</div>
			</RootLayout>,
		);
		expect(getByText("Test Content")).toBeInTheDocument();
	});
});
