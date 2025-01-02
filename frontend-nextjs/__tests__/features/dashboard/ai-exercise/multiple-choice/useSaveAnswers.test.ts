import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックデータ
const mockPayload = {
	title: "テスト問題セット",
	relatedFiles: ["file1.pdf"],
	responses: [
		{
			question_id: "1",
			question_text: "テスト問題1",
			choices: {
				choice_a: "選択肢A",
				choice_b: "選択肢B",
				choice_c: "選択肢C",
				choice_d: "選択肢D",
			},
			user_selected_choice: "A",
			correct_choice: "A",
			is_correct: true,
			explanation: "解説テキスト",
		},
	],
};

// useAuthFetchのモック
const mockFetch = vi.fn();
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => mockFetch,
}));

// 環境変数をモック
vi.stubEnv("NEXT_PUBLIC_BACKEND_HOST", "http://localhost:3000");

describe("useSaveAnswersのテスト", () => {
	beforeEach(() => {
		// 各テストの前にモックをリセット
		mockFetch.mockReset();
	});

	it("正常系: 回答データを正常に保存できる場合", async () => {
		// 成功レスポンスのモック
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve({ message: "保存成功" }),
		});

		const { result } = renderHook(() => useSaveAnswers());

		// 初期状態の確認
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
		expect(result.current.success).toBe(false);

		// saveAnswers関数を実行
		await act(async () => {
			await result.current.saveAnswers(mockPayload);
		});

		// 結果の検証
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
		expect(result.current.success).toBe(true);

		// Fetchの呼び出しを検証
		expect(mockFetch).toHaveBeenCalledWith(
			"http://localhost:3000/answers/save_answers",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(mockPayload),
			},
		);
	});

	it("異常系: APIがエラーレスポンスを返す場合", async () => {
		// エラーレスポンスのモック
		const errorMessage = "選択問題の保存に失敗しました。";
		mockFetch.mockResolvedValueOnce({
			ok: false,
			json: () => Promise.resolve({ message: errorMessage }),
		});

		const { result } = renderHook(() => useSaveAnswers());

		await act(async () => {
			await result.current.saveAnswers(mockPayload);
		});

		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBe(errorMessage);
		expect(result.current.success).toBe(false);
	});

	it("異常系: ネットワークエラーが発生する場合", async () => {
		// ネットワークエラーのモック
		mockFetch.mockRejectedValueOnce(new Error("Network Error"));

		const { result } = renderHook(() => useSaveAnswers());

		await act(async () => {
			await result.current.saveAnswers(mockPayload);
		});

		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBe("Network Error");
		expect(result.current.success).toBe(false);
	});

	it("ローディング状態が正しく変更される", async () => {
		// 遅延付きの成功レスポンスモック
		mockFetch.mockImplementation(
			() =>
				new Promise((resolve) =>
					setTimeout(
						() =>
							resolve({
								ok: true,
								json: () => Promise.resolve({ message: "保存成功" }),
							}),
						100, // 100msの遅延
					),
				),
		);

		const { result } = renderHook(() => useSaveAnswers());

		// 初期状態の確認
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
		expect(result.current.success).toBe(false);

		// 非同期処理を開始し、状態更新を待機
		await act(async () => {
			result.current.saveAnswers(mockPayload);
		});

		// ローディング状態がtrueになるのを待つ
		await waitFor(() => {
			expect(result.current.loading).toBe(true);
		});

		// 非同期処理の完了を待つ
		await waitFor(() => {
			expect(result.current.loading).toBe(false);
			expect(result.current.success).toBe(true);
		});

		// Fetchの呼び出しを検証
		expect(mockFetch).toHaveBeenCalledWith(
			"http://localhost:3000/answers/save_answers",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(mockPayload),
			},
		);
	});
});
