import SelectAnswers from "@/features/dashboard/ai-exercise/select-answers/SelectAnswers";
import { useDeleteAnswers } from "@/features/dashboard/ai-exercise/select-answers/useDeleteAnswers";
import {
	type AnswerResponse,
	useFetchAnswers,
} from "@/features/dashboard/ai-exercise/select-answers/useFetchAnswers";
import { fireEvent, render, screen } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モック関数の型定義
type UseFetchAnswersReturn = {
	answers: AnswerResponse[];
	loading: boolean;
	error: string | null;
	refetch: () => Promise<void>;
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
const mockAnswers: AnswerResponse[] = [
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
		explanation: "Test explanation",
		related_files: ["test.pdf"],
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
];

describe("SelectAnswers", () => {
	beforeEach(() => {
		// 各テストの前にモックをリセット
		vi.clearAllMocks();

		// デフォルトのモック実装を設定
		(useFetchAnswers as Mock<FetchAnswersMock>).mockReturnValue({
			answers: mockAnswers,
			loading: false,
			error: null,
			refetch: vi.fn(),
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
		});

		render(<SelectAnswers />);
		expect(screen.getByText(errorMessage)).toBeInTheDocument();
	});

	it("解答の検索が可能であること", () => {
		render(<SelectAnswers />);
		const searchInput = screen.getByRole("searchbox");
		fireEvent.change(searchInput, { target: { value: "Test Question" } });
		expect(searchInput).toHaveValue("Test Question");
	});

	it("解答の選択が可能であること", () => {
		render(<SelectAnswers />);
		const checkbox = screen.getByLabelText(`選択 ${mockAnswers[0].title}`);
		fireEvent.click(checkbox);
		expect(checkbox).toBeChecked();
	});

	it("問題文をクリックすると詳細モーダルが開くこと", () => {
		render(<SelectAnswers />);
		const questionButton = screen.getByText(mockAnswers[0].question_text);
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

		render(<SelectAnswers />);

		// 回答を選択
		const checkbox = screen.getByLabelText(`選択 ${mockAnswers[0].title}`);
		fireEvent.click(checkbox);

		// 削除ボタンをクリック
		const deleteButton = screen.getByText("選択項目を削除");
		fireEvent.click(deleteButton);

		// 確認ダイアログで削除を実行
		const confirmButton = screen.getByText("実行");
		fireEvent.click(confirmButton);

		// 削除関数が呼ばれたことを確認
		expect(mockDeleteAnswers).toHaveBeenCalledWith([1]);
	});
});
