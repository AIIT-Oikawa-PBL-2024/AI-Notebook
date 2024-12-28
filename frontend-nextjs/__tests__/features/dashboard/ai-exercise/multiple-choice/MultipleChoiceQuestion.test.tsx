import { MultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/MultipleChoiceQuestions";
import { useMultiChoiceQuestionGenerator } from "@/features/dashboard/ai-exercise/multiple-choice/useMultiChoiceQuestionGenerator";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モックの設定
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useMultiChoiceQuestionGenerator",
);
vi.mock("@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers");

// localStorage のモック
const localStorageMock = (() => {
	let store: Record<string, string> = {};
	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		},
	};
})();

Object.defineProperty(window, "localStorage", {
	value: localStorageMock,
});

describe("MultipleChoiceQuestions コンポーネント", () => {
	beforeEach(() => {
		window.localStorage.clear();
		vi.resetAllMocks();

		// useSaveAnswers のデフォルトモック値を設定
		(useSaveAnswers as Mock).mockReturnValue({
			saveAnswers: vi.fn(),
			loading: false,
			error: null,
			success: false, // 初期状態では不正解と仮定
		});
	});

	it("ロード中の状態を表示する", () => {
		(useMultiChoiceQuestionGenerator as Mock).mockReturnValue({
			loading: true,
			error: null,
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<MultipleChoiceQuestions />);

		// ローディングテキストの存在を確認
		expect(screen.getByText(/問題を生成中/)).toBeInTheDocument();

		// role="status" が存在しないため、代わりにスピナーの存在を確認
		// 例えば、SVGにaria-labelを追加している場合はそれを利用
		// ここではクラス名で確認する例を示します
		const spinner = screen.getByRole("img", { hidden: true });
		expect(spinner).toBeInTheDocument();
	});

	it("エラー状態を表示する", () => {
		(useMultiChoiceQuestionGenerator as Mock).mockReturnValue({
			loading: false,
			error: "ネットワークエラー",
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<MultipleChoiceQuestions />);

		expect(screen.getByText(/エラーが発生しました/)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /再試行/ })).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /キャッシュをクリア/ }),
		).toBeInTheDocument();
	});

	it("質問を表示する", () => {
		(useMultiChoiceQuestionGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: {
				content: [
					{
						input: {
							questions: [
								{
									question_id: "q1",
									question_text: "What is 2 + 2?",
									choices: { a: "3", b: "4", c: "5" },
									answer: "b",
									explanation: "2 + 2 equals 4.",
								},
							],
						},
					},
				],
			},
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<MultipleChoiceQuestions />);

		expect(screen.getByText(/選択問題/)).toBeInTheDocument();
		expect(
			screen.getByText(/What is 2 \+ 2\?/i, { exact: false }),
		).toBeInTheDocument();
		expect(screen.getByLabelText("3")).toBeInTheDocument();
		expect(screen.getByLabelText("4")).toBeInTheDocument();
		expect(screen.getByLabelText("5")).toBeInTheDocument();
	});

	it("不正解のみリトライする", async () => {
		const resetExerciseMock = vi.fn();
		(useMultiChoiceQuestionGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: {
				content: [
					{
						input: {
							questions: [
								{
									question_id: "q1",
									question_text: "What is 2 + 2?",
									choices: { a: "3", b: "4", c: "5" },
									answer: "b",
									explanation: "2 + 2 equals 4.",
								},
							],
						},
					},
				],
			},
			resetExercise: resetExerciseMock,
			clearCache: vi.fn(),
		});

		const mockSaveAnswers = vi.fn().mockResolvedValue({});
		(useSaveAnswers as Mock).mockReturnValue({
			saveAnswers: mockSaveAnswers,
			loading: false,
			error: "不正解です", // 不正解を示すエラーメッセージ
			success: false, // 不正解として設定
		});

		render(<MultipleChoiceQuestions />);

		// 不正解の選択肢を選ぶ
		fireEvent.click(screen.getByLabelText("3"));
		fireEvent.click(screen.getByText(/正解を確認する/));

		// リトライボタンの表示を待つ
		await waitFor(() => {
			expect(
				screen.getByRole("button", { name: /不正解のみやり直す/ }),
			).toBeInTheDocument();
		});

		// リトライボタンをクリック
		fireEvent.click(screen.getByRole("button", { name: /不正解のみやり直す/ }));

		// resetExercise が呼ばれたことを確認
		expect(resetExerciseMock).toHaveBeenCalled();
	});
});
