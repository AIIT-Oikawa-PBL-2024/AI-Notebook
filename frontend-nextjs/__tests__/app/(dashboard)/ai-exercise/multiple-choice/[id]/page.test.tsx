import GetMultipleChoiceQuestionsPage from "@/app/(dashboard)/ai-exercise/multiple-choice/[id]/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions",
	() => ({
		GetMultipleChoiceQuestions: vi.fn(() => (
			<div>Mocked GetMultipleChoiceQuestions</div>
		)),
	}),
);

describe("GetMultipleChoiceQuestionsPage", () => {
	const defaultProps: React.ComponentProps<
		typeof GetMultipleChoiceQuestionsPage
	> = {
		params: { id: "123" },
	};

	it("正しいpropsでGetMultipleChoiceQuestionsコンポーネントがレンダリングされる", () => {
		render(<GetMultipleChoiceQuestionsPage {...defaultProps} />);
		expect(
			screen.getByText("Mocked GetMultipleChoiceQuestions"),
		).toBeInTheDocument();
	});
});
