import Loading from "@/app/(dashboard)/select-files/loading";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Spinner コンポーネントのモック
vi.mock("@material-tailwind/react", () => ({
	Spinner: () => {
		return <div data-testid="mock-spinner" />;
	},
}));

describe("Loading Component", () => {
	it("should render loading spinner", () => {
		render(<Loading />);

		const spinner = screen.getByTestId("mock-spinner");
		expect(spinner).toBeInTheDocument();
	});

	it("should have correct accessibility attributes", () => {
		render(<Loading />);

		// ローディング状態を示す aria-label の確認
		const loadingContainer = screen.getByLabelText("Loading content");
		expect(loadingContainer).toBeInTheDocument();
	});

	it("should have correct styling classes", () => {
		render(<Loading />);

		const container = screen.getByLabelText("Loading content");
		expect(container).toHaveClass("flex");
		expect(container).toHaveClass("items-center");
		expect(container).toHaveClass("justify-center");
		expect(container).toHaveClass("min-h-screen");
	});
});
