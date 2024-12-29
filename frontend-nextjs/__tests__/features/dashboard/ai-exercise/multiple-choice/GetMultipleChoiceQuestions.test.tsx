import { GetMultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions";
import { useGetMultiChoiceQuestion } from "@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion";
import { useMakeSimilarQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// カスタムフックのモック
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion",
);
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions",
);
vi.mock("@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers");

// localStorageのモック
const localStorageMock = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
};
Object.defineProperty(window, "localStorage", { value: localStorageMock });

// スクロール関数のモック
window.scrollTo = vi.fn();

// サンプル問題データ
const mockQuestions = [
	{
		question_id: "1",
		question_text: "What is React?",
		choices: {
			choice_a: "A JavaScript library",
			choice_b: "A programming language",
			choice_c: "A database",
			choice_d: "An operating system",
		},
		answer: "choice_a",
		explanation: "React is a JavaScript library for building user interfaces.",
	},
];

// モック用のレスポンスデータ
const mockExercise = {
	id: "1",
	title: "Mock Exercise",
	content: [
		{
			id: "1",
			name: "Mock Exercise",
			type: "multiple_choice",
			input: {
				questions: mockQuestions,
			},
		},
	] as [
		{
			id: string;
			input: { questions: typeof mockQuestions };
			name: string;
			type: string;
		},
	],
	response: null,
	exercise_type: "multiple_choice",
	user_id: "test-user",
	created_at: new Date().toISOString(),
	files: [],
};

// モック用のレスポンスデータ
const mockExerciseData = {
	id: 1,
	title: "Mock Exercise",
	content: [
		{
			id: "1",
			name: "Mock Exercise",
			type: "multiple_choice",
			input: {
				questions: mockQuestions,
			},
		},
	] as [
		{
			id: string;
			input: { questions: typeof mockQuestions };
			name: string;
			type: string;
		},
	],
	response: "",
	exercise_type: "multiple_choice",
	user_id: "test-user",
	created_at: new Date().toISOString(),
	files: [],
};

describe("GetMultipleChoiceQuestions", () => {
	beforeEach(() => {
		vi.clearAllMocks();

		// useGetMultiChoiceQuestionのモック
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExerciseData,
			parsedResponse: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		// useMakeSimilarQuestionsのモック
		vi.mocked(useMakeSimilarQuestions).mockReturnValue({
			similarQuestions: vi.fn(),
			loading: false,
			error: null,
			exercise: mockExercise,
			success: false,
		});

		// useSaveAnswersのモック
		vi.mocked(useSaveAnswers).mockReturnValue({
			saveAnswers: vi.fn(),
			loading: false,
			error: null,
			success: false,
		});

		// localStorageのデフォルト値
		localStorageMock.getItem.mockImplementation((key) => {
			if (key === "selectedFiles") return "[]";
			return null;
		});
	});

	it("コンポーネントが正常にレンダリングされること", () => {
		render(<GetMultipleChoiceQuestions />);
		expect(screen.getByText(/選択問題/)).toBeInTheDocument();
		expect(screen.getByText("Mock Exercise")).toBeInTheDocument();
	});

	it("ローディング状態が表示されること", () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: true,
			error: "",
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetMultipleChoiceQuestions />);
		expect(screen.getByText(/問題を生成中/)).toBeInTheDocument();
	});

	it("エラー状態が表示されること", () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "テストエラー",
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetMultipleChoiceQuestions />);
		expect(screen.getByText(/エラーが発生しました/)).toBeInTheDocument();
	});

	it("回答を選択できること", () => {
		render(<GetMultipleChoiceQuestions />);
		const radio = screen.getByLabelText("A JavaScript library");
		fireEvent.click(radio);
		expect(radio).toBeChecked();
	});

	it("回答を提出して結果が表示されること", async () => {
		const mockSaveAnswers = vi.fn();
		vi.mocked(useSaveAnswers).mockReturnValue({
			saveAnswers: mockSaveAnswers,
			loading: false,
			error: null,
			success: true,
		});

		render(<GetMultipleChoiceQuestions />);

		// 回答を選択
		const radio = screen.getByLabelText("A JavaScript library");
		fireEvent.click(radio);

		// 回答を提出
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(/スコア/)).toBeInTheDocument();
			expect(mockSaveAnswers).toHaveBeenCalled();
		});
	});

	it("類似問題を生成できること", async () => {
		const mockSimilarQuestions = vi.fn();
		vi.mocked(useMakeSimilarQuestions).mockReturnValue({
			similarQuestions: mockSimilarQuestions,
			loading: false,
			error: null,
			exercise: mockExercise,
			success: false,
		});

		render(<GetMultipleChoiceQuestions />);

		// 不正解を選択
		const radio = screen.getByLabelText("A programming language");
		fireEvent.click(radio);

		// 回答を提出
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		await waitFor(() => {
			const generateButton = screen.getByText("不正解の類似問題を生成");
			fireEvent.click(generateButton);
			expect(mockSimilarQuestions).toHaveBeenCalled();
		});
	});

	it("復習モードに切り替えられること", async () => {
		render(<GetMultipleChoiceQuestions />);

		// 不正解を選択
		const radio = screen.getByLabelText("A programming language");
		fireEvent.click(radio);

		// 回答を提出
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		await waitFor(() => {
			const retryButton = screen.getByText("不正解のみやり直す");
			fireEvent.click(retryButton);
			expect(screen.getByText(/復習モード/)).toBeInTheDocument();
		});
	});

	it("全問正解の場合に類似問題生成ボタンが表示されないこと", async () => {
		render(<GetMultipleChoiceQuestions />);

		// 正解を選択
		const radio = screen.getByLabelText("A JavaScript library");
		fireEvent.click(radio);

		// 回答を提出
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		await waitFor(() => {
			expect(
				screen.queryByText("不正解の類似問題を生成"),
			).not.toBeInTheDocument();
		});
	});

	it("exerciseIdプロップが正しく渡されること", () => {
		const mockGetMultiChoiceQuestion = vi.fn().mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExerciseData,
			parsedResponse: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useGetMultiChoiceQuestion).mockImplementation(
			mockGetMultiChoiceQuestion,
		);

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);
		expect(mockGetMultiChoiceQuestion).toHaveBeenCalledWith("test-id");
	});
});
