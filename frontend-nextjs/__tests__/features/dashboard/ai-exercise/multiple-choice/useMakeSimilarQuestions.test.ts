import { useMakeSimilarQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックの型定義
const mockAuthFetch = vi.fn();
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => mockAuthFetch,
}));

// ローカルストレージのモック
const mockLocalStorage = (() => {
	let store: { [key: string]: string } = {};
	return {
		getItem: vi.fn((key: string) => store[key] || null),
		setItem: vi.fn((key: string, value: string) => {
			store[key] = value;
		}),
		clear: () => {
			store = {};
		},
	};
})();

vi.stubGlobal("localStorage", mockLocalStorage);

describe("useMakeSimilarQuestions", () => {
	beforeEach(() => {
		mockAuthFetch.mockReset();
		mockLocalStorage.clear();
	});

	// テストデータ
	const mockPayload = {
		title: "テスト問題",
		relatedFiles: ["file1.pdf"],
		responses: [
			{
				question_id: "1",
				question_text: "テスト質問",
				choices: {
					choice_a: "A",
					choice_b: "B",
					choice_c: "C",
					choice_d: "D",
				},
				user_selected_choice: "A",
				correct_choice: "A",
				is_correct: true,
				explanation: "説明",
			},
		],
	};

	const mockResponse = {
		id: "123",
		content: [
			{
				id: "1",
				input: {
					questions: [
						{
							question_id: "1",
							question_text: "類似問題",
							choices: {
								choice_a: "A",
								choice_b: "B",
								choice_c: "C",
								choice_d: "D",
							},
							answer: "A",
							explanation: "説明",
						},
					],
				},
				name: "テスト",
				type: "multiple_choice",
			},
		],
	};

	it("正常に類似問題を生成できること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockResponse),
		});

		const { result } = renderHook(() => useMakeSimilarQuestions());

		await act(async () => {
			await result.current.similarQuestions(mockPayload);
		});

		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
		expect(result.current.success).toBe(true);
		expect(result.current.exercise).toEqual(mockResponse);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
			"cached_similar_questions",
			JSON.stringify(mockResponse),
		);
	});

	it("APIエラー時の処理が正しく動作すること", async () => {
		const errorMessage = "類似問題の生成に失敗しました。";
		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
			json: () => Promise.resolve({ message: errorMessage }),
		});

		const { result } = renderHook(() => useMakeSimilarQuestions());

		await act(async () => {
			await result.current.similarQuestions(mockPayload);
		});

		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBe(errorMessage);
		expect(result.current.success).toBe(false);
	});

	it("キャッシュされた問題が正しく読み込まれること", () => {
		mockLocalStorage.getItem.mockReturnValueOnce(JSON.stringify(mockResponse));

		const { result } = renderHook(() => useMakeSimilarQuestions());

		expect(result.current.exercise).toEqual(mockResponse);
	});
});
