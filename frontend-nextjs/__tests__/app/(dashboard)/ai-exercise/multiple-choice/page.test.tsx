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

vi.mock("@/utils/withAuth", () => ({
	withAuth: vi.fn((Component) => {
		const WithAuthMock = (props: React.ComponentProps<typeof Component>) => {
			return <Component {...props} />;
		};
		return WithAuthMock;
	}),
}));

describe("MultipleChoiceQuestionsPage", () => {
	it("should render MultipleChoiceQuestions component", () => {
		render(<MultipleChoiceQuestionsPage />);

		expect(
			screen.getByText("Mocked MultipleChoiceQuestions"),
		).toBeInTheDocument();
	});

	it("should be wrapped with withAuth HOC", () => {
		render(<MultipleChoiceQuestionsPage />);

		expect(withAuth).toHaveBeenCalled();
	});

	it("should render correctly with withAuth HOC", () => {
		render(<MultipleChoiceQuestionsPage />);

		const component = screen.getByText("Mocked MultipleChoiceQuestions");
		expect(component).toBeInTheDocument();
	});
});
