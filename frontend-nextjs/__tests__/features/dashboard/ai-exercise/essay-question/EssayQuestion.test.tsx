import { EssayQuestions } from "@/features/dashboard/ai-exercise/essay-question/EssayQuestions";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import "@testing-library/jest-dom";
import { useEssayQuestionGenerator } from "@/features/dashboard/ai-exercise/essay-question/useEssayQuestionGenerator";
import { useSubmitAnswers } from "@/features/dashboard/ai-exercise/essay-question/useSubmitAnswers";
import { AuthContext } from "@/providers/AuthProvider";

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
	Spinner: () => <progress />,
	Typography: ({ children }: { children: React.ReactNode }) => (
		<div>{children}</div>
	),
	Textarea: ({
		value,
		onChange,
		disabled,
	}: {
		value: string;
		onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
		disabled?: boolean;
	}) => <textarea value={value} onChange={onChange} disabled={disabled} />,
}));

// カスタムフックのモック
vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/useEssayQuestionGenerator",
	() => ({
		useEssayQuestionGenerator: vi.fn(),
	}),
);

vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/useSubmitAnswers",
	() => ({
		useSubmitAnswers: vi.fn(),
	}),
);

const mockExercise = {
	id: "mock-exercise-id",
	exercise_id: 1,
	content: [
		{
			id: "mock-content-id",
			input: {
				questions: [
					{
						question_id: "1",
						question_text: "テスト問題1",
						answer: "回答例1",
						explanation: "この問題の解説です。",
					},
					{
						question_id: "2",
						question_text: "テスト問題2",
						answer: "回答例2",
						explanation: "この問題の解説です。",
					},
				] as const,
			},
			name: "mock-content-name",
			type: "mock-content-type",
		},
	] as [
		{
			id: string;
			input: {
				questions: {
					question_id: string;
					question_text: string;
					answer: string;
					explanation: string;
				}[];
			};
			name: string;
			type: string;
		},
	],
};

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

Object.defineProperty(window, "scrollTo", {
	value: vi.fn(),
});

// AuthContext用のモックデータ
const mockAuthContext = {
	idToken: null,
	loading: false,
	error: null,
	isAuthenticated: true,
	login: vi.fn(),
	logout: vi.fn(),
	setUser: vi.fn(),
	setIdToken: vi.fn(),
	clearError: vi.fn(),
	registerUser: vi.fn(),
	reAuthenticate: vi.fn(),
	user: {
		id: "test-user-1",
		email: "test@example.com",
		emailVerified: true,
		isAnonymous: false,
		metadata: {},
		providerId: "mock-provider-id",
		uid: "mock-uid",
		providerData: [],
		phoneNumber: null,
		displayName: "Test User",
		photoURL: null,
		refreshToken: "mock-refresh-token",
		tenantId: "mock-tenant-id",
		delete: vi.fn(),
		getIdToken: vi.fn(),
		getIdTokenResult: vi.fn(),
		linkWithCredential: vi.fn(),
		reload: vi.fn(),
		sendEmailVerification: vi.fn(),
		toJSON: vi.fn(),
	},
};

// テスト用のラッパーコンポーネント
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
	<AuthContext.Provider value={mockAuthContext}>
		{children}
	</AuthContext.Provider>
);

describe("EssayQuestions", () => {
	beforeEach(() => {
		mockLocalStorage.clear();
		vi.clearAllMocks();
	});

	it("ローディング中の表示を正しく行う", () => {
		vi.mocked(useEssayQuestionGenerator).mockReturnValue({
			loading: true,
			error: "",
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useSubmitAnswers).mockReturnValue({
			isSubmitting: false,
			error: "",
			submitAnswers: vi.fn(),
		});

		render(<EssayQuestions />, { wrapper: TestWrapper });
		expect(screen.getByRole("progressbar")).toBeInTheDocument();
		expect(screen.getByText("問題を生成中...")).toBeInTheDocument();
	});

	it("エラー時の表示を正しく行う", () => {
		const mockError = "テストエラー";
		vi.mocked(useEssayQuestionGenerator).mockReturnValue({
			loading: false,
			error: mockError,
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useSubmitAnswers).mockReturnValue({
			isSubmitting: false,
			error: "",
			submitAnswers: vi.fn(),
		});

		render(<EssayQuestions />, { wrapper: TestWrapper });
		expect(
			screen.getByText(`エラーが発生しました: ${mockError}`),
		).toBeInTheDocument();
	});

	it("問題が正しく表示される", () => {
		vi.mocked(useEssayQuestionGenerator).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useSubmitAnswers).mockReturnValue({
			isSubmitting: false,
			error: "",
			submitAnswers: vi.fn(),
		});

		render(<EssayQuestions />, { wrapper: TestWrapper });
		expect(screen.getByText(/テスト問題1$/)).toBeInTheDocument();
		expect(screen.getByText(/テスト問題2$/)).toBeInTheDocument();
	});

	it("回答を入力できる", () => {
		vi.mocked(useEssayQuestionGenerator).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useSubmitAnswers).mockReturnValue({
			isSubmitting: false,
			error: "",
			submitAnswers: vi.fn(),
		});

		render(<EssayQuestions />, { wrapper: TestWrapper });
		const textareas = screen.getAllByRole("textbox");

		fireEvent.change(textareas[0], { target: { value: "回答1" } });
		fireEvent.change(textareas[1], { target: { value: "回答2" } });

		expect(textareas[0]).toHaveValue("回答1");
		expect(textareas[1]).toHaveValue("回答2");
	});

	it("回答を送信できる", async () => {
		const mockSubmitAnswers = vi.fn().mockResolvedValue({
			scoring_results: JSON.stringify({
				content: [
					{
						input: {
							questions: [
								{
									question_id: "1",
									scoring_result: "正解",
									explanation: "良い回答です",
								},
								{
									question_id: "2",
									scoring_result: "不正解",
									explanation: "もう少し詳しく説明してください",
								},
							],
						},
					},
				],
			}),
		});

		vi.mocked(useEssayQuestionGenerator).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		vi.mocked(useSubmitAnswers).mockReturnValue({
			isSubmitting: false,
			error: "",
			submitAnswers: mockSubmitAnswers,
		});

		render(<EssayQuestions />, { wrapper: TestWrapper });
		const textareas = screen.getAllByRole("textbox");

		// 回答を入力
		fireEvent.change(textareas[0], { target: { value: "回答1" } });
		fireEvent.change(textareas[1], { target: { value: "回答2" } });

		// 送信ボタンをクリック
		const submitButton = screen.getByText("回答を送信する");
		fireEvent.click(submitButton);

		// 送信関数が呼ばれたことを確認
		expect(mockSubmitAnswers).toHaveBeenCalledWith({
			exercise_id: mockExercise.exercise_id,
			user_answer: ["回答1", "回答2"],
		});
	});
});
