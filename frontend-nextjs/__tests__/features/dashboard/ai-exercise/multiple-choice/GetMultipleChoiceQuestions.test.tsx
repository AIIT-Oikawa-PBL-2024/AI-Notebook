import { GetMultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import "@testing-library/jest-dom";
import { useGetMultiChoiceQuestion } from "@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion";

// Material Tailwindのモック
vi.mock("@material-tailwind/react", () => ({
	Alert: ({ children }: { children: React.ReactNode }) => (
		<aside>{children}</aside>
	),
	Button: ({
		children,
		onClick,
		disabled,
	}: {
		children: React.ReactNode;
		onClick?: () => void;
		disabled?: boolean;
	}) => (
		<button type="button" onClick={onClick} disabled={disabled}>
			{children}
		</button>
	),
	Card: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
	CardBody: ({ children }: { children: React.ReactNode }) => (
		<div>{children}</div>
	),
	Radio: ({
		name,
		value,
		onChange,
		disabled,
		checked,
		label,
	}: {
		name: string;
		value: string;
		onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
		disabled?: boolean;
		checked: boolean;
		label: React.ReactNode;
	}) => (
		<input
			type="radio"
			name={name}
			value={value}
			onChange={onChange}
			disabled={disabled}
			checked={checked}
			aria-label={label?.toString()}
		/>
	),
	Spinner: () => <progress />,
	Typography: ({ children }: { children: React.ReactNode }) => (
		<div>{children}</div>
	),
}));

// カスタムフックのモック
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion",
	() => ({
		useGetMultiChoiceQuestion: vi.fn(),
	}),
);

// 型定義
interface TestChoice {
	choice_a: string;
	choice_b: string;
	choice_c: string;
	choice_d: string;
}

interface TestQuestion {
	question_id: string;
	question_text: string;
	choices: TestChoice;
	answer: string;
	explanation: string;
}

interface TestParsedResponse {
	id: string;
	content: [
		{
			id: string;
			name: string;
			type: string;
			input: {
				questions: TestQuestion[];
			};
		},
	];
}

interface TestFile {
	id: string;
	file_name: string;
	file_size: string;
	created_at: string;
	user_id: string;
}

interface TestExercise {
	id: number;
	title: string;
	response: string;
	exercise_type: string;
	user_id: string;
	created_at: string;
	files: TestFile[];
}

// モックデータの修正
const mockExercise: TestExercise = {
	id: 1,
	title: "テスト問題集",
	response: "mock response",
	exercise_type: "multiple_choice",
	user_id: "test-user-1",
	created_at: "2024-01-01T00:00:00Z",
	files: [],
};

const mockParsedResponse: TestParsedResponse = {
	id: "mock-exercise-1",
	content: [
		{
			id: "content-1",
			name: "multiple-choice",
			type: "exercise",
			input: {
				questions: [
					{
						question_id: "1",
						question_text: "テスト問題1",
						choices: {
							choice_a: "選択肢1",
							choice_b: "選択肢2",
							choice_c: "選択肢3",
							choice_d: "選択肢4",
						},
						answer: "choice_a",
						explanation: "この問題の解説です。",
					},
					{
						question_id: "2",
						question_text: "テスト問題2",
						choices: {
							choice_a: "選択肢1",
							choice_b: "選択肢2",
							choice_c: "選択肢3",
							choice_d: "選択肢4",
						},
						answer: "choice_b",
						explanation: "この問題の解説です。",
					},
				],
			},
		},
	],
};

// ローカルストレージのモック
const mockLocalStorage = {
	store: {} as Record<string, string>,
	getItem(key: string) {
		return this.store[key] || null;
	},
	setItem(key: string, value: string) {
		this.store[key] = value;
	},
	removeItem(key: string) {
		delete this.store[key];
	},
	clear() {
		this.store = {};
	},
};

Object.defineProperty(window, "localStorage", {
	value: mockLocalStorage,
});

// window.scrollTo のモック
Object.defineProperty(window, "scrollTo", {
	value: vi.fn(),
});

describe("GetMultipleChoiceQuestions", () => {
	beforeEach(() => {
		mockLocalStorage.clear();
		vi.clearAllMocks();
	});

	it("ローディング中の表示を正しく行う", () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: true,
			error: "",
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);
		expect(screen.getByRole("progressbar")).toBeInTheDocument();
		expect(screen.getByText("問題を生成中...")).toBeInTheDocument();
	});

	it("エラー時の表示を正しく行う", () => {
		const mockError = "テストエラー";
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: mockError,
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);
		expect(
			screen.getByText(`エラーが発生しました: ${mockError}`),
		).toBeInTheDocument();
	});

	it("問題が正しく表示される", () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);
		expect(screen.getByText(mockExercise.title)).toBeInTheDocument();
		expect(screen.getByText(/テスト問題1$/)).toBeInTheDocument();
		expect(screen.getByText(/テスト問題2$/)).toBeInTheDocument();
	});

	it("回答を選択して提出できる", async () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		const radios = screen.getAllByRole("radio");
		const question1Choice = radios[0]; // 1問目の選択肢A
		const question2Choice = radios[5]; // 2問目の選択肢B

		fireEvent.click(question1Choice);
		fireEvent.click(question2Choice);

		const submitButton = screen.getByText("回答を確認する");
		expect(submitButton).not.toBeDisabled();

		fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(/スコア: \d+ \/ \d+/)).toBeInTheDocument();
			expect(window.scrollTo).toHaveBeenCalledWith({
				top: 0,
				behavior: "smooth",
			});
		});
	});

	it("不正解のみやり直しができる", async () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		// 一問目を間違える（選択肢B）、二問目は正解（選択肢B）
		const radios = screen.getAllByRole("radio");
		fireEvent.click(radios[1]);
		fireEvent.click(radios[5]);

		fireEvent.click(screen.getByText("回答を確認する"));

		await waitFor(() => {
			const retryButton = screen.getByText("不正解のみやり直す");
			fireEvent.click(retryButton);
		});

		expect(screen.getByText("選択問題（復習モード）")).toBeInTheDocument();
		expect(screen.queryByText(/テスト問題2$/)).not.toBeInTheDocument();
	});

	it("ローカルストレージに回答が保存される", async () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		const radios = screen.getAllByRole("radio");
		fireEvent.click(radios[0]); // 最初の問題の最初の選択肢を選択

		const cachedAnswers = JSON.parse(
			mockLocalStorage.getItem("cached_answers") || "{}",
		);
		expect(cachedAnswers).toHaveProperty("1", "choice_a");
	});

	it("exerciseIdなしでもコンポーネントが正しく動作する", () => {
		vi.mocked(useGetMultiChoiceQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions />);
		expect(screen.getByText(mockExercise.title)).toBeInTheDocument();
	});
});
