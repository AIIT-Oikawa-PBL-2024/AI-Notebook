import ClientThemeProvider from "@/providers/ClientThemeProvider";
import { render } from "@testing-library/react";
import type React from "react";
import { describe, expect, it, vi } from "vitest";

// ThemeProviderをモック化
vi.mock("@material-tailwind/react", () => ({
	ThemeProvider: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="theme-provider">{children}</div>
	),
}));

describe("ClientThemeProvider", () => {
	it("子要素がThemeProviderでラップされてレンダリングされること", () => {
		const testChild = <div>Test Child</div>;
		const { getByTestId, getByText } = render(
			<ClientThemeProvider>{testChild}</ClientThemeProvider>,
		);

		// ThemeProviderが正しくレンダリングされていることを確認
		const themeProvider = getByTestId("theme-provider");
		expect(themeProvider).toBeDefined();

		// 子要素が正しくレンダリングされていることを確認
		const child = getByText("Test Child");
		expect(child).toBeDefined();
	});
});
