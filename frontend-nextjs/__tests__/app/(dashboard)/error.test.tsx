import DashboardError from "@/app/(dashboard)/error";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

type AlertProps = {
	children: ReactNode;
	icon?: ReactNode;
	className?: string;
	variant?: "filled" | "gradient" | "ghost" | "static";
	color?: "blue" | "red" | "green" | "orange" | "purple" | "pink";
};

// Material Tailwindのコンポーネントのモック
vi.mock("@material-tailwind/react", () => ({
	Alert: ({ children, icon, className }: AlertProps) => (
		<div data-testid="alert" className={className}>
			{icon}
			{children}
		</div>
	),
}));

describe("DashboardError", () => {
	it("正常系: エラーメッセージが表示される", () => {
		render(<DashboardError />);
		expect(
			screen.getByText("エラーが発生しました。もう一度お試しください。"),
		).toBeInTheDocument();
	});

	it("正常系: アイコンが表示される", () => {
		render(<DashboardError />);
		const svg = screen.getByRole("img", { name: "error" });
		expect(svg).toBeInTheDocument();
	});

	it("正常系: 適切なスタイルが適用されている", () => {
		render(<DashboardError />);
		const container = screen.getByTestId("alert").parentElement;
		expect(container).toHaveClass(
			"flex items-start mt-32 justify-center min-h-screen text-center",
		);
	});
});
