import EssayQuestionsPage from "@/app/(dashboard)/ai-exercise/essay-question/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/EssayQuestions",
	() => ({
		EssayQuestions: vi.fn(() => <div>Mocked EssayQuestions</div>),
	}),
);

describe("EssayQuestionsPage", () => {
	it("EssayQuestionsコンポーネントがレンダリングされるべき", () => {
		render(<EssayQuestionsPage />);

		expect(screen.getByText("Mocked EssayQuestions")).toBeInTheDocument();
	});
});
