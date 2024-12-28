import SelectedAnswers from "@/features/dashboard/ai-exercise/select-answers/answers/SelectedAnswers";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックデータ
const mockAnswers = [
	{
		id: 1,
		title: "テスト問題1",
		related_files: [],
		question_id: "q1",
		question_text: "これはテスト問題です。",
		choice_a: "選択肢A",
		choice_b: "選択肢B",
		choice_c: "選択肢C",
		choice_d: "選択肢D",
		correct_choice: "choice_a",
		explanation: "これは解説です。",
		user_id: "user1",
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
];

// モック
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: vi.fn(),
	}),
}));

// localStorage モック
const mockLocalStorage = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	clear: vi.fn(),
};
Object.defineProperty(window, "localStorage", {
	value: mockLocalStorage,
});

describe("SelectedAnswers", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify(mockAnswers));
	});

	it("問題が正しく表示される", () => {
		render(<SelectedAnswers />);
		expect(screen.getByText("テスト問題1")).toBeInTheDocument();
		expect(screen.getByText("これはテスト問題です。")).toBeInTheDocument();
	});

	it("選択肢が正しく表示される", () => {
		render(<SelectedAnswers />);
		expect(screen.getByText(/選択肢A/)).toBeInTheDocument();
		expect(screen.getByText(/選択肢B/)).toBeInTheDocument();
		expect(screen.getByText(/選択肢C/)).toBeInTheDocument();
		expect(screen.getByText(/選択肢D/)).toBeInTheDocument();
	});

	it("選択肢を選んで正解を確認できる", () => {
		render(<SelectedAnswers />);

		// 選択肢Aを選択
		const radioA = screen.getByLabelText(/A\. 選択肢A/);
		fireEvent.click(radioA);

		// 正解確認ボタンをクリック
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// 正解メッセージが表示される
		expect(screen.getByText("正解です！")).toBeInTheDocument();
	});

	it("不正解の場合、適切なメッセージが表示される", () => {
		render(<SelectedAnswers />);

		// 選択肢B（不正解）を選択
		const radioB = screen.getByLabelText(/B\. 選択肢B/);
		fireEvent.click(radioB);

		// 正解確認ボタンをクリック
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// 不正解メッセージが表示される
		expect(screen.getByText(/不正解です/)).toBeInTheDocument();
	});

	it("リセットボタンで状態がリセットされる", () => {
		render(<SelectedAnswers />);

		// 選択肢を選択して正解確認
		const radioA = screen.getByLabelText(/A\. 選択肢A/);
		fireEvent.click(radioA);
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// リセットボタンをクリック
		const resetButton = screen.getByText("リセット");
		fireEvent.click(resetButton);

		// 正解/不正解の表示が消えている
		expect(screen.queryByText("正解です！")).not.toBeInTheDocument();
	});

	it("LocalStorageにデータが保存される", () => {
		render(<SelectedAnswers />);

		// 選択肢を選択して正解確認
		const radioA = screen.getByLabelText(/A\. 選択肢A/);
		fireEvent.click(radioA);
		const submitButton = screen.getByText("正解を確認する");
		fireEvent.click(submitButton);

		// LocalStorageが呼ばれたことを確認
		expect(mockLocalStorage.setItem).toHaveBeenCalled();
	});

	it("LocalStorageのデータが空の場合エラーメッセージが表示される", () => {
		mockLocalStorage.getItem.mockReturnValue(null);
		render(<SelectedAnswers />);

		expect(
			screen.getByText("選択された解答が見つかりません。"),
		).toBeInTheDocument();
	});
});
