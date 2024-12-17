import GetEssayQuestionsPage from "@/app/(dashboard)/ai-exercise/essay-question/[id]/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/GetEssayQuestions",
	() => ({
		GetEssayQuestions: vi.fn(() => <div>Mocked GetEssayQuestions</div>),
	}),
);

describe("GetEssayQuestionsPage", () => {
	const defaultProps: React.ComponentProps<typeof GetEssayQuestionsPage> = {
		params: { id: "123" },
	};

	it("正しいpropsでGetEssayQuestionsコンポーネントがレンダリングされる", () => {
		render(<GetEssayQuestionsPage {...defaultProps} />);
		expect(screen.getByText("Mocked GetEssayQuestions")).toBeInTheDocument();
	});
});
