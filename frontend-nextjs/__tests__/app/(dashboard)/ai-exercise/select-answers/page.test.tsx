import SelectAnswersPage from "@/app/(dashboard)/ai-exercise/select-answers/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// 依存関係をモック化
vi.mock(
	"@/features/dashboard/ai-exercise/select-answers/SelectAnswers",
	() => ({
		default: vi.fn(() => <div>Mocked SelectAnswersComponent</div>),
	}),
);

describe("SelectAnswersPage", () => {
	it("SelectAnswersComponentが正しくレンダリングされること", () => {
		render(<SelectAnswersPage />);

		expect(
			screen.getByText("Mocked SelectAnswersComponent"),
		).toBeInTheDocument();
	});
});
