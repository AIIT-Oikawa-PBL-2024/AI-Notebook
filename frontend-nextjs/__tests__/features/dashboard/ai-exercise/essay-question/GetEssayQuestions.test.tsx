import { GetEssayQuestions } from "@/features/dashboard/ai-exercise/essay-question/GetEssayQuestions";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import "@testing-library/jest-dom";
import { useGetEssayQuestion } from "@/features/dashboard/ai-exercise/essay-question/useGetEssayQuestion";
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
	}: {
		value: string;
		onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
	}) => <textarea value={value} onChange={onChange} />,
}));

// useSubmitAnswersのモック
vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/useSubmitAnswers",
	() => ({
		useSubmitAnswers: () => ({
			error: "",
			submitAnswers: vi.fn().mockResolvedValue({
				scoring_results: JSON.stringify({
					content: [
						{
							input: {
								questions: [],
								refreshToken: "mock-refresh-token",
								delete: vi.fn(),
								getIdToken: vi.fn(),
								getIdTokenResult: vi.fn(),
								linkWithCredential: vi.fn(),
								reload: vi.fn(),
								toJSON: vi.fn(),
							},
						},
					],
				}),
			}),
		}),
	}),
);

// カスタムフックのモック
vi.mock(
	"@/features/dashboard/ai-exercise/essay-question/useGetEssayQuestion",
	() => ({
		useGetEssayQuestion: vi.fn(),
	}),
);

const mockExercise = {
	id: 1,
	title: "テスト問題集",
	response: "mock response",
	exercise_type: "essay-question",
	user_id: "test-user-1",
	created_at: "2024-01-01T00:00:00Z",
	files: [],
};

const mockParsedResponse = {
	id: "mock-exercise-1",
	content: [
		{
			id: "content-1",
			name: "essay-question",
			type: "exercise",
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
				],
			},
		},
	] as [
		{
			id: string;
			name: string;
			type: string;
			input: {
				questions: {
					question_id: string;
					question_text: string;
					answer: string;
					explanation: string;
				}[];
			};
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
	user: {
		providerId: "mock-provider-id",
		uid: "test-user-1",
		email: "test@example.com",
		emailVerified: true,
		isAnonymous: false,
		metadata: {},
		providerData: [],
		phoneNumber: null,
		displayName: null,
		photoURL: null,
		tenantId: null,
		refreshToken: "mock-refresh-token",
		delete: vi.fn(),
		getIdToken: vi.fn(),
		getIdTokenResult: vi.fn(),
		linkWithCredential: vi.fn(),
		reload: vi.fn(),
		toJSON: vi.fn(),
	},
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
};

// テスト用のラッパーコンポーネント
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
	<AuthContext.Provider value={mockAuthContext}>
		{children}
	</AuthContext.Provider>
);

describe("GetEssayQuestions", () => {
	beforeEach(() => {
		mockLocalStorage.clear();
		vi.clearAllMocks();
	});

	it("ローディング中の表示を正しく行う", () => {
		vi.mocked(useGetEssayQuestion).mockReturnValue({
			loading: true,
			error: "",
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetEssayQuestions exerciseId="test-id" />, {
			wrapper: TestWrapper,
		});
		expect(screen.getByRole("progressbar")).toBeInTheDocument();
		expect(screen.getByText("問題を生成中...")).toBeInTheDocument();
	});

	it("エラー時の表示を正しく行う", () => {
		const mockError = "テストエラー";
		vi.mocked(useGetEssayQuestion).mockReturnValue({
			loading: false,
			error: mockError,
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetEssayQuestions exerciseId="test-id" />, {
			wrapper: TestWrapper,
		});
		expect(
			screen.getByText(`エラーが発生しました: ${mockError}`),
		).toBeInTheDocument();
	});

	it("問題が正しく表示される", () => {
		vi.mocked(useGetEssayQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetEssayQuestions exerciseId="test-id" />, {
			wrapper: TestWrapper,
		});
		expect(screen.getByText(mockExercise.title)).toBeInTheDocument();
		expect(screen.getByText(/テスト問題1$/)).toBeInTheDocument();
		expect(screen.getByText(/テスト問題2$/)).toBeInTheDocument();
	});

	it("回答を入力できる", () => {
		vi.mocked(useGetEssayQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetEssayQuestions exerciseId="test-id" />, {
			wrapper: TestWrapper,
		});
		const textareas = screen.getAllByRole("textbox");

		fireEvent.change(textareas[0], { target: { value: "回答1" } });
		fireEvent.change(textareas[1], { target: { value: "回答2" } });

		expect(textareas[0]).toHaveValue("回答1");
		expect(textareas[1]).toHaveValue("回答2");
	});

	it("exerciseIdなしでもコンポーネントが正しく動作する", () => {
		vi.mocked(useGetEssayQuestion).mockReturnValue({
			loading: false,
			error: "",
			exercise: mockExercise,
			parsedResponse: mockParsedResponse,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
			checkCache: () => ({ exercise: null, generationStatus: null }),
		});

		render(<GetEssayQuestions />, { wrapper: TestWrapper });
		expect(screen.getByText(mockExercise.title)).toBeInTheDocument();
	});
});
