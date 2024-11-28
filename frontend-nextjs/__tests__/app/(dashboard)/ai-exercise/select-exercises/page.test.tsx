import SelectExercisesPage from "@/app/(dashboard)/ai-exercise/select-exercises/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// 依存関係をモック化
vi.mock(
	"@/features/dashboard/ai-exercise/select-exercises/SelectExercises",
	() => ({
		default: vi.fn(() => <div>Mocked ExerciseSelectComponent</div>),
	}),
);

describe("SelectExercisesPage", () => {
	it("ExerciseSelectComponentが正しくレンダリングされること", () => {
		render(<SelectExercisesPage />);

		expect(
			screen.getByText("Mocked ExerciseSelectComponent"),
		).toBeInTheDocument();
	});
});
