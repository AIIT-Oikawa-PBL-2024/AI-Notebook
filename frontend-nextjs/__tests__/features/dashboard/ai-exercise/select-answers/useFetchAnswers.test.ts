import { useFetchAnswers } from "@/features/dashboard/ai-exercise/select-answers/useFetchAnswers";
import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックデータ
const mockAnswers = [
	{
		id: 1,
		title: "テスト回答1",
		related_files: ["file1.pdf"],
		question_id: "1",
		question_text: "テスト問題1",
		choice_a: "選択肢A",
		choice_b: "選択肢B",
		choice_c: "選択肢C",
		choice_d: "選択肢D",
		user_selected_choice: "A",
		correct_choice: "A",
		is_correct: true,
		explanation: "解説テキスト",
		user_id: "user1",
		created_at: "2024-01-01T00:00:00Z",
		updated_at: "2024-01-01T00:00:00Z",
	},
];

// useAuthFetchのモック
const mockFetch = vi.fn();
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => mockFetch,
}));

describe("useFetchAnswersのテスト", () => {
	beforeEach(() => {
		// 各テストの前にモックをリセット
		mockFetch.mockReset();
	});

	it("正常系: 回答データを正常に取得できる場合", async () => {
		// モックの実装: フックが期待する形式でレスポンスを返す
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () =>
				Promise.resolve({ total: mockAnswers.length, answers: mockAnswers }),
		});

		// フックをレンダリング
		const { result } = renderHook(() => useFetchAnswers());

		// 初期状態の確認
		expect(result.current.loading).toBe(true);
		expect(result.current.error).toBe("");

		// データ取得完了まで待機
		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		// 結果の検証
		expect(result.current.answers).toEqual(mockAnswers);
		expect(result.current.error).toBe("");
		expect(result.current.totalCount).toBe(mockAnswers.length);
		expect(result.current.currentPage).toBe(1);
		expect(result.current.totalPages).toBe(Math.ceil(mockAnswers.length / 10)); // 初期limitは10
	});

	it("異常系: APIがエラーレスポンスを返す場合", async () => {
		// エラーレスポンスのモック
		mockFetch.mockResolvedValueOnce({
			ok: false,
		});

		const { result } = renderHook(() => useFetchAnswers());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("回答データの取得に失敗しました");
		expect(result.current.answers).toEqual([]);
	});

	it("異常系: ネットワークエラーが発生する場合", async () => {
		// ネットワークエラーのモック
		mockFetch.mockRejectedValueOnce(new Error("Network Error"));

		const { result } = renderHook(() => useFetchAnswers());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("Network Error");
		expect(result.current.answers).toEqual([]);
	});

	it("refetch関数: データを再取得できることを確認", async () => {
		// 初回取得のモック
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () =>
				Promise.resolve({ total: mockAnswers.length, answers: mockAnswers }),
		});

		const { result } = renderHook(() => useFetchAnswers());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		// 2回目の取得のモック: 新しいデータを返す
		const updatedMockAnswers = [
			...mockAnswers,
			{
				id: 2,
				title: "テスト回答2",
				related_files: ["file2.pdf"],
				question_id: "2",
				question_text: "テスト問題2",
				choice_a: "選択肢A2",
				choice_b: "選択肢B2",
				choice_c: "選択肢C2",
				choice_d: "選択肢D2",
				user_selected_choice: "B",
				correct_choice: "C",
				is_correct: false,
				explanation: "解説テキスト2",
				user_id: "user1",
				created_at: "2024-01-02T00:00:00Z",
				updated_at: "2024-01-02T00:00:00Z",
			},
		];

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () =>
				Promise.resolve({
					total: updatedMockAnswers.length,
					answers: updatedMockAnswers,
				}),
		});

		// refetch関数を実行 (例: ページ2、limit10)
		result.current.refetch(2, 10);

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		// 結果の検証
		expect(result.current.answers).toEqual(updatedMockAnswers);
		expect(result.current.totalCount).toBe(updatedMockAnswers.length);
		expect(result.current.currentPage).toBe(2);
		expect(result.current.totalPages).toBe(
			Math.ceil(updatedMockAnswers.length / 10),
		);
	});
});
