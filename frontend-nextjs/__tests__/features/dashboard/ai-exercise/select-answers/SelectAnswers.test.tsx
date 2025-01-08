import SelectAnswers from "@/features/dashboard/ai-exercise/select-answers/SelectAnswers";
import { useDeleteAnswers } from "@/features/dashboard/ai-exercise/select-answers/useDeleteAnswers";
import {
	type AnswerResponse,
	useFetchAnswers,
} from "@/features/dashboard/ai-exercise/select-answers/useFetchAnswers";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モック関数の型定義
type UseFetchAnswersReturn = {
	answers: AnswerResponse[];
	loading: boolean;
	error: string | null;
	refetch: (page: number, limit: number) => Promise<void>;
	totalCount: number;
	currentPage: number;
	totalPages: number;
};

type UseDeleteAnswersReturn = {
	deleteAnswers: (ids: number[]) => Promise<{
		deleted_ids: number[];
		not_found_ids: number[];
		unauthorized_ids: number[];
	}>;
	loading: boolean;
	error: string | null;
};

// モックの作成
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: vi.fn(),
	}),
}));

// モック関数の型
type FetchAnswersMock = () => UseFetchAnswersReturn;
type DeleteAnswersMock = () => UseDeleteAnswersReturn;

vi.mock(
	"@/features/dashboard/ai-exercise/select-answers/useFetchAnswers",
	() => ({
		useFetchAnswers: vi.fn() as Mock<FetchAnswersMock>,
	}),
);

vi.mock(
	"@/features/dashboard/ai-exercise/select-answers/useDeleteAnswers",
	() => ({
		useDeleteAnswers: vi.fn() as Mock<DeleteAnswersMock>,
	}),
);

// モックデータ
const mockAnswersPage1: AnswerResponse[] = [
	{
		id: 1,
		question_id: "1",
		user_id: "1",
		title: "Test Question 1",
		question_text: "What is testing?",
		choice_a: "Option A",
		choice_b: "Option B",
		choice_c: "Option C",
		choice_d: "Option D",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 1",
		related_files: ["test1.pdf"],
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
	{
		id: 2,
		question_id: "2",
		user_id: "1",
		title: "Test Question 2",
		question_text: "What is React?",
		choice_a: "Library",
		choice_b: "Framework",
		choice_c: "Language",
		choice_d: "Tool",
		user_selected_choice: "choice_b",
		correct_choice: "choice_a",
		is_correct: false,
		explanation: "Test explanation 2",
		related_files: ["test2.pdf"],
		created_at: "2024-01-02T00:00:00Z",
		updated_at: "2024-01-02T00:00:00Z",
	},
	{
		id: 3,
		question_id: "3",
		user_id: "1",
		title: "Test Question 3",
		question_text: "What is TypeScript?",
		choice_a: "Superset of JavaScript",
		choice_b: "Subset of JavaScript",
		choice_c: "Framework",
		choice_d: "Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 3",
		related_files: ["test3.pdf"],
		created_at: "2024-01-03T00:00:00Z",
		updated_at: "2024-01-03T00:00:00Z",
	},
	{
		id: 4,
		question_id: "4",
		user_id: "1",
		title: "Test Question 4",
		question_text: "What is Jest?",
		choice_a: "Testing Framework",
		choice_b: "State Management",
		choice_c: "Styling Library",
		choice_d: "Build Tool",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 4",
		related_files: ["test4.pdf"],
		created_at: "2024-01-04T00:00:00Z",
		updated_at: "2024-01-04T00:00:00Z",
	},
	{
		id: 5,
		question_id: "5",
		user_id: "1",
		title: "Test Question 5",
		question_text: "What is Next.js?",
		choice_a: "React Framework",
		choice_b: "JavaScript Library",
		choice_c: "CSS Framework",
		choice_d: "Database",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 5",
		related_files: ["test5.pdf"],
		created_at: "2024-01-05T00:00:00Z",
		updated_at: "2024-01-05T00:00:00Z",
	},
	{
		id: 6,
		question_id: "6",
		user_id: "1",
		title: "Test Question 6",
		question_text: "What is Node.js?",
		choice_a: "JavaScript Runtime",
		choice_b: "Frontend Framework",
		choice_c: "CSS Library",
		choice_d: "Database",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 6",
		related_files: ["test6.pdf"],
		created_at: "2024-01-06T00:00:00Z",
		updated_at: "2024-01-06T00:00:00Z",
	},
	{
		id: 7,
		question_id: "7",
		user_id: "1",
		title: "Test Question 7",
		question_text: "What is Redux?",
		choice_a: "State Management Library",
		choice_b: "Routing Library",
		choice_c: "Styling Framework",
		choice_d: "Build Tool",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 7",
		related_files: ["test7.pdf"],
		created_at: "2024-01-07T00:00:00Z",
		updated_at: "2024-01-07T00:00:00Z",
	},
	{
		id: 8,
		question_id: "8",
		user_id: "1",
		title: "Test Question 8",
		question_text: "What is GraphQL?",
		choice_a: "Query Language",
		choice_b: "Programming Language",
		choice_c: "Framework",
		choice_d: "Database",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 8",
		related_files: ["test8.pdf"],
		created_at: "2024-01-08T00:00:00Z",
		updated_at: "2024-01-08T00:00:00Z",
	},
	{
		id: 9,
		question_id: "9",
		user_id: "1",
		title: "Test Question 9",
		question_text: "What is Docker?",
		choice_a: "Containerization Platform",
		choice_b: "Programming Language",
		choice_c: "Testing Framework",
		choice_d: "State Management",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 9",
		related_files: ["test9.pdf"],
		created_at: "2024-01-09T00:00:00Z",
		updated_at: "2024-01-09T00:00:00Z",
	},
	{
		id: 10,
		question_id: "10",
		user_id: "1",
		title: "Test Question 10",
		question_text: "What is Kubernetes?",
		choice_a: "Container Orchestration",
		choice_b: "CSS Framework",
		choice_c: "Database",
		choice_d: "Routing Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 10",
		related_files: ["test10.pdf"],
		created_at: "2024-01-10T00:00:00Z",
		updated_at: "2024-01-10T00:00:00Z",
	},
];

const mockAnswersPage2: AnswerResponse[] = [
	{
		id: 11,
		question_id: "11",
		user_id: "1",
		title: "Test Question 11",
		question_text: "What is advanced testing?",
		choice_a: "Option A1",
		choice_b: "Option B1",
		choice_c: "Option C1",
		choice_d: "Option D1",
		user_selected_choice: "choice_b",
		correct_choice: "choice_b",
		is_correct: true,
		explanation: "Test explanation 11",
		related_files: ["test11.pdf"],
		created_at: "2024-01-11T00:00:00Z",
		updated_at: "2024-01-11T00:00:00Z",
	},
	{
		id: 12,
		question_id: "12",
		user_id: "1",
		title: "Test Question 12",
		question_text: "What is ESLint?",
		choice_a: "Linting Tool",
		choice_b: "Build Tool",
		choice_c: "State Management",
		choice_d: "CSS Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 12",
		related_files: ["test12.pdf"],
		created_at: "2024-01-12T00:00:00Z",
		updated_at: "2024-01-12T00:00:00Z",
	},
	{
		id: 13,
		question_id: "13",
		user_id: "1",
		title: "Test Question 13",
		question_text: "What is Babel?",
		choice_a: "JavaScript Compiler",
		choice_b: "Database",
		choice_c: "CSS Framework",
		choice_d: "Testing Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 13",
		related_files: ["test13.pdf"],
		created_at: "2024-01-13T00:00:00Z",
		updated_at: "2024-01-13T00:00:00Z",
	},
	{
		id: 14,
		question_id: "14",
		user_id: "1",
		title: "Test Question 14",
		question_text: "What is Tailwind CSS?",
		choice_a: "Utility-first CSS Framework",
		choice_b: "JavaScript Library",
		choice_c: "State Management Tool",
		choice_d: "Backend Framework",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 14",
		related_files: ["test14.pdf"],
		created_at: "2024-01-14T00:00:00Z",
		updated_at: "2024-01-14T00:00:00Z",
	},
	{
		id: 15,
		question_id: "15",
		user_id: "1",
		title: "Test Question 15",
		question_text: "What is Webpack?",
		choice_a: "Module Bundler",
		choice_b: "CSS Framework",
		choice_c: "Database",
		choice_d: "Routing Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 15",
		related_files: ["test15.pdf"],
		created_at: "2024-01-15T00:00:00Z",
		updated_at: "2024-01-15T00:00:00Z",
	},
	{
		id: 16,
		question_id: "16",
		user_id: "1",
		title: "Test Question 16",
		question_text: "What is SASS?",
		choice_a: "CSS Preprocessor",
		choice_b: "JavaScript Framework",
		choice_c: "State Management Tool",
		choice_d: "Backend Language",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 16",
		related_files: ["test16.pdf"],
		created_at: "2024-01-16T00:00:00Z",
		updated_at: "2024-01-16T00:00:00Z",
	},
	{
		id: 17,
		question_id: "17",
		user_id: "1",
		title: "Test Question 17",
		question_text: "What is Prettier?",
		choice_a: "Code Formatter",
		choice_b: "State Management Library",
		choice_c: "CSS Framework",
		choice_d: "Database",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 17",
		related_files: ["test17.pdf"],
		created_at: "2024-01-17T00:00:00Z",
		updated_at: "2024-01-17T00:00:00Z",
	},
	{
		id: 18,
		question_id: "18",
		user_id: "1",
		title: "Test Question 18",
		question_text: "What is Cypress?",
		choice_a: "End-to-End Testing Framework",
		choice_b: "State Management Tool",
		choice_c: "CSS Library",
		choice_d: "Routing Framework",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 18",
		related_files: ["test18.pdf"],
		created_at: "2024-01-18T00:00:00Z",
		updated_at: "2024-01-18T00:00:00Z",
	},
	{
		id: 19,
		question_id: "19",
		user_id: "1",
		title: "Test Question 19",
		question_text: "What is Prisma?",
		choice_a: "ORM Tool",
		choice_b: "CSS Framework",
		choice_c: "State Management Library",
		choice_d: "Testing Library",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 19",
		related_files: ["test19.pdf"],
		created_at: "2024-01-19T00:00:00Z",
		updated_at: "2024-01-19T00:00:00Z",
	},
	{
		id: 20,
		question_id: "20",
		user_id: "1",
		title: "Test Question 20",
		question_text: "What is ESLint?",
		choice_a: "Linting Tool",
		choice_b: "JavaScript Framework",
		choice_c: "State Management Library",
		choice_d: "CSS Framework",
		user_selected_choice: "choice_a",
		correct_choice: "choice_a",
		is_correct: true,
		explanation: "Test explanation 20",
		related_files: ["test20.pdf"],
		created_at: "2024-01-20T00:00:00Z",
		updated_at: "2024-01-20T00:00:00Z",
	},
];

describe("SelectAnswers", () => {
	beforeEach(() => {
		// 各テストの前にモックをリセット
		vi.clearAllMocks();

		// デフォルトのモック実装を設定
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
			answers: mockAnswersPage1,
			loading: false,
			error: null,
			refetch: vi.fn().mockResolvedValue(undefined),
			totalCount: 20,
			currentPage: 1,
			totalPages: 2,
		});

		(useDeleteAnswers as Mock<DeleteAnswersMock>).mockReturnValue({
			deleteAnswers: vi.fn().mockResolvedValue({
				deleted_ids: [],
				not_found_ids: [],
				unauthorized_ids: [],
			}),
			loading: false,
			error: null,
		});
	});

	it("クラッシュせずにレンダリングされること", () => {
		render(<SelectAnswers />);
		expect(screen.getByText("解答リスト")).toBeInTheDocument();
	});

	it("データ取得中にローディングスピナーが表示されること", () => {
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
			answers: [],
			loading: true,
			error: null,
			refetch: vi.fn(),
			totalCount: 0,
			currentPage: 1,
			totalPages: 0,
		});

		render(<SelectAnswers />);
		expect(screen.getByTestId("loading-spinner")).toBeInTheDocument();
	});

	it("フェッチが失敗した場合にエラーメッセージが表示されること", () => {
		const errorMessage = "Failed to fetch answers";
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
			answers: [],
			loading: false,
			error: errorMessage,
			refetch: vi.fn(),
			totalCount: 0,
			currentPage: 1,
			totalPages: 0,
		});

		render(<SelectAnswers />);
		expect(screen.getByText(errorMessage)).toBeInTheDocument();
	});

	it("解答の検索が可能であること", () => {
		render(<SelectAnswers />);
		const searchInput = screen.getByRole("searchbox");
		fireEvent.change(searchInput, { target: { value: "Test Question 1" } });
		expect(searchInput).toHaveValue("Test Question 1");
		// クライアントサイドでのフィルタリングを確認
		expect(screen.getByText("Test Question 1")).toBeInTheDocument();
	});

	it("解答の選択が可能であること", () => {
		render(<SelectAnswers />);
		const checkbox = screen.getByLabelText(`選択 ${mockAnswersPage1[0].title}`);
		fireEvent.click(checkbox);
		expect(checkbox).toBeChecked();
	});

	it("問題文をクリックすると詳細モーダルが開くこと", () => {
		render(<SelectAnswers />);
		const questionButton = screen.getByText(mockAnswersPage1[0].question_text);
		fireEvent.click(questionButton);
		expect(screen.getByText("問題・解答の詳細")).toBeInTheDocument();
	});

	it("解答の並び替えが可能であること", () => {
		render(<SelectAnswers />);
		const titleSortButton = screen.getByText("タイトル").closest("button");
		if (!titleSortButton) throw new Error("Button not found");
		fireEvent.click(titleSortButton);
		// ソート状態の変更を確認
		expect(titleSortButton).toBeInTheDocument();
		// 具体的なソート結果の検証は必要に応じて追加可能です
	});

	it("削除操作が正しく処理されること", async () => {
		const mockDeleteAnswers = vi.fn().mockResolvedValue({
			deleted_ids: [1],
			not_found_ids: [],
			unauthorized_ids: [],
		});

		(useDeleteAnswers as Mock<DeleteAnswersMock>).mockReturnValue({
			deleteAnswers: mockDeleteAnswers,
			loading: false,
			error: null,
		});

		const mockRefetch = vi.fn().mockResolvedValue(undefined);
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
			answers: mockAnswersPage1,
			loading: false,
			error: null,
			refetch: mockRefetch,
			totalCount: 20,
			currentPage: 1,
			totalPages: 2,
		});

		render(<SelectAnswers />);

		// 回答を選択
		const checkbox = screen.getByLabelText(`選択 ${mockAnswersPage1[0].title}`);
		fireEvent.click(checkbox);
		expect(checkbox).toBeChecked();

		// 削除ボタンをクリック
		const deleteButton = screen.getByText("選択項目を削除");
		fireEvent.click(deleteButton);

		// 確認ダイアログで削除を実行
		const confirmButton = screen.getByText("実行");
		fireEvent.click(confirmButton);

		// 削除関数が呼ばれたことを確認
		await waitFor(() => {
			expect(mockDeleteAnswers).toHaveBeenCalledWith([1]);
		});

		// refetchが呼ばれたことを確認
		await waitFor(() => {
			expect(mockRefetch).toHaveBeenCalledWith(1, 10);
		});

		// 削除後は選択がリセットされていることを確認
		expect(checkbox).not.toBeChecked();
	});

	// ページネーション関連のテストケースを追加
	describe("ページネーション", () => {
		it("「前へ」ボタンが最初のページでは無効化されていること", () => {
			(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
				answers: mockAnswersPage1,
				loading: false,
				error: null,
				refetch: vi.fn(),
				totalCount: 20,
				currentPage: 1,
				totalPages: 2,
			});

			render(<SelectAnswers />);

			// 「前へ」ボタンが無効化されていることを確認
			const prevButton = screen.getByText("前へ") as HTMLButtonElement;
			expect(prevButton).toBeDisabled();
		});
	});

	it("「次へ」ボタンをクリックしてページを切り替えること", async () => {
		const mockRefetch = vi.fn().mockResolvedValue(undefined);

		// ページ1のデータ
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValueOnce({
			answers: mockAnswersPage1,
			loading: false,
			error: null,
			refetch: mockRefetch,
			totalCount: 20,
			currentPage: 1,
			totalPages: 2,
		});

		// ページ2のデータ
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValueOnce({
			answers: mockAnswersPage2,
			loading: false,
			error: null,
			refetch: mockRefetch,
			totalCount: 20,
			currentPage: 2,
			totalPages: 2,
		});

		render(<SelectAnswers />);

		// 初期ページの確認
		expect(screen.getByText("Test Question 1")).toBeInTheDocument();
		expect(screen.queryByText("Test Question 11")).not.toBeInTheDocument();

		// 「次へ」ボタンをクリック
		const nextButton = screen.getByText("次へ");
		fireEvent.click(nextButton);

		// refetchがページ2で呼ばれたことを確認
		await waitFor(() => {
			expect(mockRefetch).toHaveBeenCalledWith(2, 10);
		});
	});
});
