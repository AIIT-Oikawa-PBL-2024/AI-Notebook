import GetExercisePage from "@/app/(dashboard)/ai-exercise/stream/[id]/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("@/features/dashboard/ai-exercise/stream/GetExerciseDisplay", () => ({
	GetExerciseDisplay: vi.fn(() => <div>Mocked GetExerciseDisplay</div>),
}));

vi.mock("@/utils/withAuth", () => ({
	withAuth: vi.fn((Component) => {
		const WithAuthMock = (props: React.ComponentProps<typeof Component>) => {
			return <Component {...props} />;
		};
		return WithAuthMock;
	}),
}));

describe("GetExercisePage", () => {
	const defaultProps: React.ComponentProps<typeof GetExercisePage> = {
		params: { id: "123" },
	};

	it("should render GetExerciseDisplay component with correct props", () => {
		render(<GetExercisePage {...defaultProps} />);
		expect(screen.getByText("Mocked GetExerciseDisplay")).toBeInTheDocument();
	});

	it("should be wrapped with withAuth HOC", () => {
		render(<GetExercisePage {...defaultProps} />);
		expect(withAuth).toHaveBeenCalled();
	});

	it("should render correctly with withAuth HOC", () => {
		render(<GetExercisePage {...defaultProps} />);
		const component = screen.getByText("Mocked GetExerciseDisplay");
		expect(component).toBeInTheDocument();
	});
});
