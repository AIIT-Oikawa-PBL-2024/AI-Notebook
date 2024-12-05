import CreateExercisePage from "@/app/(dashboard)/ai-exercise/stream/page";
import { ExerciseDisplay } from "@/features/dashboard/ai-exercise/stream/ExerciseDisplay";
import { useExerciseGenerator } from "@/features/dashboard/ai-exercise/stream/useExerciseGenerator";
import { render, screen, waitFor } from "@testing-library/react";
import { ErrorBoundary } from "react-error-boundary";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// useExerciseGeneratorのモック
vi.mock("@/features/dashboard/ai-exercise/stream/useExerciseGenerator", () => ({
	useExerciseGenerator: vi.fn(),
}));

// ExerciseDisplayのモック
vi.mock("@/features/dashboard/ai-exercise/stream/ExerciseDisplay", () => ({
	ExerciseDisplay: vi.fn(({ loading, error, exercise, title }) => (
		<div data-testid="exercise-display">Exercise Display</div>
	)),
}));

describe("CreateExercisePage", () => {
	beforeEach(() => {
		vi.resetModules();
		vi.restoreAllMocks();

		// デフォルトのモック値を設定
		(useExerciseGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: null,
			title: "",
			resetExercise: vi.fn(),
		});
	});

	const renderWithWrapper = (ui: React.ReactElement) => {
		return render(ui, {
			wrapper: ({ children }) => (
				<ErrorBoundary fallback={<div>Error occurred</div>}>
					{children}
				</ErrorBoundary>
			),
		});
	};

	it("正常系: ローディング中の状態を表示できる", () => {
		(useExerciseGenerator as Mock).mockReturnValue({
			loading: true,
			error: null,
			exercise: null,
			title: "",
			resetExercise: vi.fn(),
		});

		renderWithWrapper(<CreateExercisePage />);

		expect(ExerciseDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: true,
				error: null,
				exercise: null,
				title: "",
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
			title: "テストタイトル",
			resetExercise: vi.fn(),
		});

		renderWithWrapper(<CreateExercisePage />);

		await waitFor(() => {
			expect(ExerciseDisplay).toHaveBeenCalledWith(
				expect.objectContaining({
					loading: false,
					error: null,
					exercise: mockExercise,
					title: "テストタイトル",
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
			title: "",
			resetExercise: vi.fn(),
		});

		renderWithWrapper(<CreateExercisePage />);

		expect(ExerciseDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: false,
				error: mockError,
				exercise: null,
				title: "",
			}),
			expect.anything(),
		);
	});

	it("正常系: コンテナのスタイルが正しく適用されている", () => {
		renderWithWrapper(<CreateExercisePage />);

		const containerDiv = screen.getByTestId("exercise-page-container");
		expect(containerDiv).toHaveClass("container", "mx-auto", "p-4");
	});

	it("正常系: ExerciseDisplayコンポーネントが適切にレンダリングされる", () => {
		renderWithWrapper(<CreateExercisePage />);

		// もし直接data-testidが見つからない場合は、レンダリング結果をデバッグ
		screen.debug();

		// ExerciseDisplayが呼び出されたことを確認
		expect(ExerciseDisplay).toHaveBeenCalled();
	});
});
