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

vi.mock("@/utils/withAuth", () => ({
	withAuth: vi.fn((Component) => {
		const WithAuthMock = (props: React.ComponentProps<typeof Component>) => {
			return <Component {...props} />;
		};
		return WithAuthMock;
	}),
}));

describe("GetMultipleChoiceQuestionsPage", () => {
	const defaultProps: React.ComponentProps<
		typeof GetMultipleChoiceQuestionsPage
	> = {
		params: { id: "123" },
	};

	it("should render GetMultipleChoiceQuestions component with correct props", () => {
		render(<GetMultipleChoiceQuestionsPage {...defaultProps} />);
		expect(
			screen.getByText("Mocked GetMultipleChoiceQuestions"),
		).toBeInTheDocument();
	});

	it("should be wrapped with withAuth HOC", () => {
		render(<GetMultipleChoiceQuestionsPage {...defaultProps} />);
		expect(withAuth).toHaveBeenCalled();
	});

	it("should render correctly with withAuth HOC", () => {
		render(<GetMultipleChoiceQuestionsPage {...defaultProps} />);
		const component = screen.getByText("Mocked GetMultipleChoiceQuestions");
		expect(component).toBeInTheDocument();
	});
});
