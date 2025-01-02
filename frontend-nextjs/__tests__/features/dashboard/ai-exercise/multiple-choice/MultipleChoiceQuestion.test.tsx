import { MultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/MultipleChoiceQuestions";
import type {
	Choice,
	ExerciseResponse,
	Question,
} from "@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions";
import { useMakeSimilarQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions";
import { useMultiChoiceQuestionGenerator } from "@/features/dashboard/ai-exercise/multiple-choice/useMultiChoiceQuestionGenerator";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// カスタムフックのモック
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useMultiChoiceQuestionGenerator",
);
vi.mock("@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers");
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions",
);

// localStorageのモック
const localStorageMock = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// 正しい型構造を持つサンプル問題のモック
const mockQuestions: Question[] = [
	{
		question_id: "1",
		question_text: "What is React?",
		choices: {
			choice_a: "A JavaScript library",
			choice_b: "A programming language",
			choice_c: "A database",
			choice_d: "An operating system",
		} as Choice,
		answer: "choice_a",
		explanation: "React is a JavaScript library for building user interfaces.",
	},
];

// 演習レスポンス型のモック
const mockExercise: ExerciseResponse = {
	id: "mock-exercise-1",
	content: [
		{
			id: "1",
			name: "Mock Exercise",
			type: "multiple_choice",
			input: {
				questions: mockQuestions,
			},
		},
	],
};

describe("MultipleChoiceQuestions", () => {
	beforeEach(() => {
		// 各テスト前にすべてのモックをリセット
		vi.clearAllMocks();

		// 正しい型を持つデフォルトのフック戻り値をモック
		vi.mocked(useMultiChoiceQuestionGenerator).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn().mockReturnValue({
				exercise: null,
				generationStatus: null,
			}),
		});

		vi.mocked(useSaveAnswers).mockReturnValue({
			saveAnswers: vi.fn(),
			loading: false,
			error: null,
			success: false,
		});

		// useMakeSimilarQuestionsのモックを追加
		vi.mocked(useMakeSimilarQuestions).mockReturnValue({
			similarQuestions: async (payload) => {
				/* モックの実装 */
			},
			loading: false,
			error: null,
			success: false,
			exercise: mockExercise,
		});

		// localStorageのデフォルト値をモック
		localStorageMock.getItem.mockImplementation((key) => {
			if (key === "title") return "Test Title";
			if (key === "selectedFiles") return "[]";
			return null;
		});
	});

	it("問題なくレンダリングされること", () => {
		render(<MultipleChoiceQuestions />);
		expect(screen.getByText(/選択問題/)).toBeInTheDocument();
	});

	it("ローディング状態が表示されること", () => {
		vi.mocked(useMultiChoiceQuestionGenerator).mockReturnValue({
			loading: true,
			error: "",
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn().mockReturnValue({
				exercise: null,
				generationStatus: null,
			}),
		});

		vi.mocked(useMakeSimilarQuestions).mockReturnValue({
			similarQuestions: async (payload) => {
				/* モックの実装 */
			},
			loading: true,
			error: null,
			exercise: null,
			success: false,
		});

		render(<MultipleChoiceQuestions />);
		expect(screen.getByText(/問題を生成中/)).toBeInTheDocument();
	});

	it("エラー状態が表示されること", () => {
		vi.mocked(useMultiChoiceQuestionGenerator).mockReturnValue({
			loading: false,
			error: "テストエラー",
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn().mockReturnValue({
				exercise: null,
				generationStatus: null,
			}),
		});

		vi.mocked(useMakeSimilarQuestions).mockReturnValue({
			similarQuestions: async (payload) => {
				/* モックの実装 */
			},
			loading: false,
			error: "類似問題エラー",
			success: false,
			exercise: null,
		});

		render(<MultipleChoiceQuestions />);
		expect(screen.getByText(/エラーが発生しました/)).toBeInTheDocument();
	});

	it("回答の選択ができること", () => {
		render(<MultipleChoiceQuestions />);

		const radio = screen.getByLabelText("A JavaScript library");
		fireEvent.click(radio);

		expect(radio).toBeChecked();
	});

	it("送信ボタンをクリックすると結果が表示されること", async () => {
		const { saveAnswers } = useSaveAnswers();
		render(<MultipleChoiceQuestions />);

		// 回答を選択
		const radio = screen.getByLabelText("A JavaScript library");
		fireEvent.click(radio);

		// 送信ボタンをクリック
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// 結果が表示されるまで待機
		await waitFor(() => {
			expect(screen.getByText(/スコア/)).toBeInTheDocument();
			expect(saveAnswers).toHaveBeenCalled();
		});
	});

	it("復習モードが正しく動作すること", async () => {
		render(<MultipleChoiceQuestions />);

		// 誤答を選択
		const radio = screen.getByLabelText("A programming language");
		fireEvent.click(radio);

		// 回答を送信
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// リトライボタンをクリック
		await waitFor(() => {
			const retryButton = screen.getByText("不正解のみやり直す");
			fireEvent.click(retryButton);
			expect(screen.getByText(/復習モード/)).toBeInTheDocument();
		});
	});
});
