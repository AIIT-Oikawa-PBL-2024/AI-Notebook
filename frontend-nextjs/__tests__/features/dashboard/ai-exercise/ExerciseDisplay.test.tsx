import { ExerciseDisplay } from "@/features/dashboard/ai-exercise/ExerciseDisplay";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock material-tailwind components
vi.mock("@material-tailwind/react", () => ({
	Alert: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="alert">{children}</div>
	),
	Card: ({
		children,
		...props
	}: { children: React.ReactNode; [key: string]: unknown }) => (
		<div data-testid="card" {...props}>
			{children}
		</div>
	),
	CardBody: ({
		children,
		...props
	}: { children: React.ReactNode; [key: string]: unknown }) => (
		<div data-testid="card-body" {...props}>
			{children}
		</div>
	),
	CardHeader: ({
		children,
		...props
	}: { children: React.ReactNode; [key: string]: unknown }) => (
		<div data-testid="card-header" {...props}>
			{children}
		</div>
	),
	Spinner: ({ ...props }) => <div data-testid="spinner" {...props} />,
	Typography: ({
		children,
		...props
	}: { children: React.ReactNode; [key: string]: unknown }) => (
		<div data-testid="typography" {...props}>
			{children}
		</div>
	),
}));

describe("ExerciseDisplay", () => {
	// ローディング状態のテスト
	it("displays spinner when loading and no error", () => {
		render(<ExerciseDisplay loading={true} error="" exercise="" />);
		expect(screen.getByTestId("spinner")).toBeDefined();
	});

	// エラー状態のテスト
	it("displays error message when there is an error", () => {
		const errorMessage = "テストエラーメッセージ";
		render(
			<ExerciseDisplay loading={false} error={errorMessage} exercise="" />,
		);
		expect(screen.getByTestId("alert")).toBeDefined();
		expect(screen.getByText(errorMessage)).toBeDefined();
	});

	// 問題文表示のテスト
	it("displays exercise content with markdown formatting", () => {
		const exerciseContent = `
# テスト問題
## セクション1
これは問題文です。

* 項目1
* 項目2

1. 手順1
2. 手順2
    `;

		render(
			<ExerciseDisplay loading={false} error="" exercise={exerciseContent} />,
		);

		// 見出しのテスト
		expect(screen.getByText("テスト問題")).toBeDefined();
		expect(screen.getByText("セクション1")).toBeDefined();

		// 本文のテスト
		expect(screen.getByText("これは問題文です。")).toBeDefined();

		// リストアイテムのテスト
		expect(screen.getByText("項目1")).toBeDefined();
		expect(screen.getByText("項目2")).toBeDefined();
		expect(screen.getByText("手順1")).toBeDefined();
		expect(screen.getByText("手順2")).toBeDefined();
	});

	// エラーがある場合はスピナーを表示しないことをテスト
	it("does not show spinner when there is an error", () => {
		render(<ExerciseDisplay loading={true} error="エラー" exercise="" />);
		expect(screen.queryByTestId("spinner")).toBeNull();
		expect(screen.getByTestId("alert")).toBeDefined();
	});

	// コンポーネントの基本構造のテスト
	it("renders with correct structure", () => {
		render(<ExerciseDisplay loading={false} error="" exercise="" />);
		expect(screen.getByTestId("card")).toBeDefined();
		expect(screen.getByTestId("card-header")).toBeDefined();
		expect(screen.getByTestId("card-body")).toBeDefined();
		expect(screen.getByText("AI 練習問題")).toBeDefined();
	});

	// 空の状態のテスト
	it("renders empty state correctly", () => {
		render(<ExerciseDisplay loading={false} error="" exercise="" />);
		expect(screen.queryByTestId("spinner")).toBeNull();
		expect(screen.queryByTestId("alert")).toBeNull();
		expect(screen.getByTestId("card-body")).toBeDefined();
	});
});
