import { MarkdownPreview } from "@/features/dashboard/notebook/components/MarkdownPreview";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// ReactMarkdownのモック
vi.mock("react-markdown", () => ({
	default: ({ children }: { children: string }) => (
		<div data-testid="markdown-content">{children}</div>
	),
}));

// XMarkIconのモック
vi.mock("@heroicons/react/24/solid", () => ({
	XMarkIcon: () => <span data-testid="close-icon">CloseIcon</span>,
}));

describe("MarkdownPreview", () => {
	const mockTitle = "テストタイトル";
	const mockContent = "# テスト本文";
	const mockOnClose = vi.fn();

	beforeEach(() => {
		mockOnClose.mockClear();
	});

	it("タイトルと本文が正しくレンダリングされること", () => {
		render(
			<MarkdownPreview
				title={mockTitle}
				content={mockContent}
				onClose={mockOnClose}
			/>,
		);

		// タイトルの確認
		expect(screen.getByText(mockTitle)).toBeInTheDocument();

		// 本文の確認
		expect(screen.getByTestId("markdown-content")).toHaveTextContent(
			mockContent,
		);
	});

	it("タイトルが未指定の場合、デフォルトタイトルが表示されること", () => {
		render(
			<MarkdownPreview title="" content={mockContent} onClose={mockOnClose} />,
		);

		expect(screen.getByText("無題のノート")).toBeInTheDocument();
	});

	it("本文が未指定の場合、デフォルトメッセージが表示されること", () => {
		render(
			<MarkdownPreview title={mockTitle} content="" onClose={mockOnClose} />,
		);

		expect(screen.getByTestId("markdown-content")).toHaveTextContent(
			"本文がありません",
		);
	});

	it("閉じるボタンをクリックするとonCloseが呼ばれること", () => {
		render(
			<MarkdownPreview
				title={mockTitle}
				content={mockContent}
				onClose={mockOnClose}
			/>,
		);

		const closeButton = screen.getByRole("button");
		fireEvent.click(closeButton);

		expect(mockOnClose).toHaveBeenCalledTimes(1);
	});
});
