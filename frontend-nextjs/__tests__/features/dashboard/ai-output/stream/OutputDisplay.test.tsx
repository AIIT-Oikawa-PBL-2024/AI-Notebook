// FILE: OutputDisplay.test.tsx
import { OutputDisplay } from "@/features/dashboard/ai-output/stream/OutputDisplay";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import "@testing-library/jest-dom";

// Mock ReactMarkdown
vi.mock("react-markdown", () => ({
	default: ({
		children,
		components,
	}: {
		children: string;
		components: { [key: string]: React.ElementType };
	}) => <div data-testid="markdown">{children}</div>,
}));

// Mock material-tailwind components
vi.mock("@material-tailwind/react", () => ({
	Alert: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="alert">{children}</div>
	),
	Card: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="card">{children}</div>
	),
	CardBody: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="card-body">{children}</div>
	),
	CardHeader: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="card-header">{children}</div>
	),
	Spinner: () => <div data-testid="spinner" />,
	Typography: ({ children }: { children: React.ReactNode }) => (
		<span>{children}</span>
	),
}));

describe("OutputDisplay", () => {
	it("displays spinner when loading and no error", () => {
		render(<OutputDisplay loading={true} error="" output="" />);
		expect(screen.getByTestId("spinner")).toBeInTheDocument();
	});

	it("displays error message when there is an error", () => {
		const errorMessage = "テストエラーメッセージ";
		render(<OutputDisplay loading={false} error={errorMessage} output="" />);
		expect(screen.getByTestId("alert")).toBeInTheDocument();
		expect(screen.getByText(errorMessage)).toBeInTheDocument();
	});

	it("displays output content with markdown formatting", () => {
		const outputContent = "# テスト問題\n## セクション1\nこれは問題文です。";
		render(<OutputDisplay loading={false} error="" output={outputContent} />);
		const markdownElement = screen.getByTestId("markdown");
		// 空白文字を正規化して比較
		expect(markdownElement.textContent?.replace(/\s+/g, " ").trim()).toBe(
			"# テスト問題 ## セクション1 これは問題文です。",
		);
	});

	it("renders with correct structure", () => {
		render(<OutputDisplay loading={false} error="" output="" />);
		expect(screen.getByTestId("card")).toBeInTheDocument();
		expect(screen.getByTestId("card-header")).toBeInTheDocument();
		expect(screen.getByTestId("card-body")).toBeInTheDocument();
		expect(screen.getByText("AI ノート")).toBeInTheDocument();
	});
});
