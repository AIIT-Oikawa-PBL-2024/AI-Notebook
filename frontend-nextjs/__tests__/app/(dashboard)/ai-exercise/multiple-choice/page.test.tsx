import MultipleChoiceQuestionsPage from "@/app/(dashboard)/ai-exercise/multiple-choice/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/MultipleChoiceQuestions",
	() => ({
		MultipleChoiceQuestions: vi.fn(() => (
			<div>Mocked MultipleChoiceQuestions</div>
		)),
	}),
);

describe("MultipleChoiceQuestionsPage", () => {
	it("MultipleChoiceQuestionsコンポーネントがレンダリングされるべき", () => {
		render(<MultipleChoiceQuestionsPage />);

		expect(
			screen.getByText("Mocked MultipleChoiceQuestions"),
		).toBeInTheDocument();
	});
});
