import CreateExercisePage from "@/app/(dashboard)/ai-exercise/page";
import { ExerciseDisplay } from "@/features/dashboard/ai-exercise/ExerciseDisplay";
import { useExerciseGenerator } from "@/features/dashboard/ai-exercise/useExerciseGenerator";
import { render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// useExerciseGeneratorのモック
vi.mock("@/features/dashboard/ai-exercise/useExerciseGenerator", () => ({
	useExerciseGenerator: vi.fn(),
}));

// withAuthのモック
vi.mock("@/utils/withAuth", () => ({
	withAuth: (Component: React.ComponentType) => Component,
}));

// ExerciseDisplayのモック
vi.mock("@/features/dashboard/ai-exercise/ExerciseDisplay", () => ({
	ExerciseDisplay: vi.fn(() => (
		<div data-testid="exercise-display">Exercise Display</div>
	)),
}));

describe("CreateExercisePage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("正常系: ローディング中の状態を表示できる", () => {
		// useExerciseGeneratorの返り値をモック
		(useExerciseGenerator as Mock).mockReturnValue({
			loading: true,
			error: null,
			exercise: null,
		});

		render(<CreateExercisePage />);

		expect(ExerciseDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: true,
				error: null,
				exercise: null,
			}),
			expect.anything(),
		);
	});

	it("正常系: エクササイズデータを表示できる", async () => {
		const mockExercise = {
			id: "1",
			title: "テストエクササイズ",
			description: "テスト説明",
		};

		(useExerciseGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: mockExercise,
		});

		render(<CreateExercisePage />);

		await waitFor(() => {
			expect(ExerciseDisplay).toHaveBeenCalledWith(
				expect.objectContaining({
					loading: false,
					error: null,
					exercise: mockExercise,
				}),
				expect.anything(),
			);
		});
	});

	it("異常系: エラー状態を表示できる", () => {
		const mockError = new Error("テストエラー");

		(useExerciseGenerator as Mock).mockReturnValue({
			loading: false,
			error: mockError,
			exercise: null,
		});

		render(<CreateExercisePage />);

		expect(ExerciseDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: false,
				error: mockError,
				exercise: null,
			}),
			expect.anything(),
		);
	});

	it("正常系: コンテナのスタイルが正しく適用されている", () => {
		(useExerciseGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: null,
		});

		render(<CreateExercisePage />);

		const container = screen.getByTestId("exercise-display").parentElement;
		expect(container).toHaveClass("container", "mx-auto", "p-4");
	});

	it("正常系: ExerciseDisplayコンポーネントが適切にレンダリングされる", () => {
		(useExerciseGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: null,
		});

		render(<CreateExercisePage />);

		expect(screen.getByTestId("exercise-display")).toBeInTheDocument();
	});
});
