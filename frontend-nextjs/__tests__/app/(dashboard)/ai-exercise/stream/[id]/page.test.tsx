import GetExercisePage from "@/app/(dashboard)/ai-exercise/stream/[id]/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("@/features/dashboard/ai-exercise/stream/GetExerciseDisplay", () => ({
	GetExerciseDisplay: vi.fn(() => <div>Mocked GetExerciseDisplay</div>),
}));

describe("GetExercisePage", () => {
	const defaultProps: React.ComponentProps<typeof GetExercisePage> = {
		params: { id: "123" },
	};

	it("GetExerciseDisplayコンポーネントが正しいpropsでレンダリングされること", () => {
		render(<GetExercisePage {...defaultProps} />);
		expect(screen.getByText("Mocked GetExerciseDisplay")).toBeInTheDocument();
	});
});
