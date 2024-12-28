import { GetMultipleChoiceQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/GetMultipleChoiceQuestions";
import { useGetMultiChoiceQuestion } from "@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モックの設定
vi.mock(
	"@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion",
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

describe("GetMultipleChoiceQuestions コンポーネント", () => {
	beforeEach(() => {
		window.localStorage.clear();
		vi.resetAllMocks();

		// useSaveAnswers のデフォルトモック値を設定
		(useSaveAnswers as Mock).mockReturnValue({
			saveAnswers: vi.fn(),
			loading: false,
			error: null,
			success: false,
		});
	});

	it("ロード中の状態を表示する", () => {
		(useGetMultiChoiceQuestion as Mock).mockReturnValue({
			loading: true,
			error: null,
			exercise: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions />);

		// ローディングテキストの存在を確認
		expect(screen.getByText(/問題を生成中/)).toBeInTheDocument();

		// role="status" が存在しないため、代わりにスピナーの存在を確認
		// 例えば、SVGにaria-labelを追加している場合はそれを利用
		// ここではクラス名で確認する例を示します
		const spinner = screen.getByRole("img", { hidden: true });
		expect(spinner).toBeInTheDocument();
	});

	it("エラー状態を表示する", () => {
		(useGetMultiChoiceQuestion as Mock).mockReturnValue({
			loading: false,
			error: "エラーが発生しました",
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		expect(screen.getByText(/エラーが発生しました/)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /再試行/ })).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /キャッシュをクリア/ }),
		).toBeInTheDocument();
	});

	it("問題が見つからない状態を表示する", () => {
		(useGetMultiChoiceQuestion as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: null,
			parsedResponse: null,
			resetExercise: vi.fn(),
			clearCache: vi.fn(),
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		expect(screen.getByText(/問題が見つかりません/)).toBeInTheDocument();
		expect(screen.getByRole("button", { name: /再試行/ })).toBeInTheDocument();
	});

	it("問題を表示して回答を送信する", async () => {
		(useGetMultiChoiceQuestion as Mock).mockReturnValue({
			loading: false,
			error: null,
			exercise: { title: "テスト問題" },
			parsedResponse: {
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

		const saveAnswersMock = vi.fn().mockResolvedValue({});
		(useSaveAnswers as Mock).mockReturnValue({
			saveAnswers: saveAnswersMock,
			loading: false,
			error: null,
			success: true,
		});

		render(<GetMultipleChoiceQuestions exerciseId="test-id" />);

		expect(screen.getByText(/What is 2 \+ 2\?/i)).toBeInTheDocument();

		// ユーザーの選択
		fireEvent.click(screen.getByLabelText("4"));
		expect((screen.getByLabelText("4") as HTMLInputElement).checked).toBe(true);

		// 回答の送信
		fireEvent.click(screen.getByText(/正解を確認する/));
		await waitFor(() => {
			expect(saveAnswersMock).toHaveBeenCalled();
		});

		// 結果表示
		expect(screen.getByText(/スコア: 1 \/ 1/)).toBeInTheDocument();
		expect(screen.getByText(/2 \+ 2 equals 4\./)).toBeInTheDocument();
	});
});
