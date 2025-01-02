import AnswersPage from "@/app/(dashboard)/ai-exercise/select-answers/answers/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// 依存関係をモック化
vi.mock(
	"@/features/dashboard/ai-exercise/select-answers/answers/SelectedAnswers",
	() => ({
		default: vi.fn(() => <div>Mocked SelectedAnswersComponent</div>),
	}),
);

describe("AnswersPage", () => {
	it("SelectedAnswersComponentが正しくレンダリングされること", () => {
		render(<AnswersPage />);

		expect(
			screen.getByText("Mocked SelectedAnswersComponent"),
		).toBeInTheDocument();
	});
});
