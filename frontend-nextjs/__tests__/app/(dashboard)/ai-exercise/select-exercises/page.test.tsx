import SelectExercisesPage from "@/app/(dashboard)/ai-exercise/select-exercises/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock(
	"@/features/dashboard/ai-exercise/select-exercises/SelectExercises",
	() => ({
		default: vi.fn(() => <div>Mocked ExerciseSelectComponent</div>),
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

describe("SelectExercisesPage", () => {
	it("should render ExerciseSelectComponent", () => {
		render(<SelectExercisesPage />);

		expect(
			screen.getByText("Mocked ExerciseSelectComponent"),
		).toBeInTheDocument();
	});

	it("should be wrapped with withAuth HOC", () => {
		render(<SelectExercisesPage />);

		expect(withAuth).toHaveBeenCalled();
	});

	it("should render correctly with withAuth HOC", () => {
		render(<SelectExercisesPage />);

		const component = screen.getByText("Mocked ExerciseSelectComponent");
		expect(component).toBeInTheDocument();
	});
});
