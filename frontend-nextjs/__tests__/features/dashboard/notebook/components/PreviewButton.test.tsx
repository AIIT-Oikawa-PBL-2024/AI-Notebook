import { PreviewButton } from "@/features/dashboard/notebook/components/PreviewButton";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// モックの作成
vi.mock("@heroicons/react/24/solid", () => ({
	EyeIcon: () => <span data-testid="eye-icon">EyeIcon</span>,
}));

describe("PreviewButton", () => {
	it("ボタンが正しくレンダリングされること", () => {
		render(<PreviewButton />);

		// ボタンのテキストが存在することを確認
		expect(screen.getByText("プレビュー")).toBeInTheDocument();

		// アイコンが存在することを確認
		expect(screen.getByTestId("eye-icon")).toBeInTheDocument();
	});

	it("クリックイベントが正しく発火すること", () => {
		// モックの関数を作成
		const mockOnClick = vi.fn();

		render(<PreviewButton onClick={mockOnClick} />);

		// ボタンを取得してクリック
		const button = screen.getByRole("button");
		fireEvent.click(button);

		// クリックイベントが1回呼ばれたことを確認
		expect(mockOnClick).toHaveBeenCalledTimes(1);
	});
});
