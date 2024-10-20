import { BackgroundCard } from "@/components/layouts/BackgroundCard";
import { render, screen } from "@testing-library/react";
import type React from "react";
import { describe, expect, it, vi } from "vitest";

// Material Tailwindコンポーネントのモック
vi.mock("@material-tailwind/react", () => ({
	Card: vi.fn(
		({
			children,
			className,
			shadow,
			...props
		}: React.HTMLProps<HTMLDivElement> & { shadow?: boolean }) => (
			<div data-testid="card" className={className} {...props}>
				{children}
			</div>
		),
	),
	CardHeader: vi.fn(
		({
			children,
			className,
			floated,
			shadow,
			color,
			...props
		}: React.HTMLProps<HTMLDivElement> & {
			floated?: boolean;
			shadow?: boolean;
			color?: string;
		}) => (
			<div data-testid="card-header" className={className} {...props}>
				{children}
			</div>
		),
	),
	CardBody: vi.fn(
		({ children, className, ...props }: React.HTMLProps<HTMLDivElement>) => (
			<div data-testid="card-body" className={className} {...props}>
				{children}
			</div>
		),
	),
	Typography: vi.fn(
		({
			children,
			variant,
			color,
			className,
			...props
		}: React.HTMLProps<HTMLDivElement> & {
			variant?: string;
			color?: string;
		}) => (
			<div
				data-testid={`typography-${variant}`}
				className={className}
				style={{ color }}
				{...props}
			>
				{children}
			</div>
		),
	),
}));

describe("BackgroundCard", () => {
	it("正しい構造でレンダリングされる", () => {
		render(<BackgroundCard />);
		expect(screen.getByTestId("card")).toBeInTheDocument();
		expect(screen.getByTestId("card-header")).toBeInTheDocument();
		expect(screen.getByTestId("card-body")).toBeInTheDocument();
	});

	it("Cardコンポーネントに正しいプロパティが設定されている", () => {
		render(<BackgroundCard />);
		const card = screen.getByTestId("card");
		expect(card).toHaveClass(
			"relative grid h-[40rem] w-full max-w-[28rem] items-end justify-center overflow-hidden text-center",
		);
	});

	it("CardHeaderに正しいプロパティが設定されている", () => {
		render(<BackgroundCard />);
		const cardHeader = screen.getByTestId("card-header");
		expect(cardHeader).toHaveClass(
			"absolute inset-0 m-0 h-full w-full rounded-none bg-[url('/ai-notebook2.jpg')] bg-cover bg-center",
		);
	});

	it("CardHeaderの子要素に正しいグラデーションクラスが設定されている", () => {
		render(<BackgroundCard />);
		const gradientDiv = screen.getByTestId("card-header")
			.firstChild as HTMLElement;
		expect(gradientDiv).toHaveClass(
			"to-bg-black-10 absolute inset-0 h-full w-full bg-gradient-to-t from-black/80 via-black/50",
		);
	});

	it("CardBodyに正しいクラスが設定されている", () => {
		render(<BackgroundCard />);
		const cardBody = screen.getByTestId("card-body");
		expect(cardBody).toHaveClass("relative py-14 px-6 md:px-12");
	});

	it("タイトルのTypographyコンポーネントに正しいプロパティが設定されている", () => {
		render(<BackgroundCard />);
		const title = screen.getByText("AI Notebook");
		expect(title).toHaveAttribute("data-testid", "typography-h2");
		expect(title).toHaveClass("mb-6 font-medium leading-[1.5]");

		const computedStyle = getComputedStyle(title);
		const color = computedStyle.getPropertyValue("color");
		expect(color).toMatch(/^(white|#fff(fff)?|rgb\(255,\s*255,\s*255\))$/i);
	});

	it("サブタイトルのTypographyコンポーネントに正しいプロパティが設定されている", () => {
		render(<BackgroundCard />);
		const subtitle = screen.getByText("OikawaPBL 2024");
		expect(subtitle).toHaveAttribute("data-testid", "typography-h5");
		expect(subtitle).toHaveClass("mb-4 text-gray-400");
	});
});
