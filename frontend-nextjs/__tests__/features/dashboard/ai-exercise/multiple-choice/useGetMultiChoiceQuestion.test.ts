import { useGetMultiChoiceQuestion } from "@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mockデータ
const mockExercise = {
	id: 1,
	title: "Test Exercise",
	response: JSON.stringify({
		content: [
			{
				id: "1",
				input: {
					questions: [
						{
							question_id: "1",
							question_text: "Test Question",
							choices: {
								choice_a: "A",
								choice_b: "B",
								choice_c: "C",
								choice_d: "D",
							},
							answer: "A",
							explanation: "Test Explanation",
						},
					],
				},
				name: "Test",
				type: "multiple_choice",
			},
		],
	}),
	exercise_type: "multiple_choice",
	user_id: "1",
	created_at: "2024-01-01",
	files: [],
};

// モックの設定
const mockFetch = vi.fn();
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => mockFetch,
}));

// ローカルストレージのモック
const mockLocalStorage = {
	store: {} as { [key: string]: string },
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

describe("useGetMultiChoiceQuestion", () => {
	beforeEach(() => {
		// テスト前の初期化
		vi.clearAllMocks();
		mockLocalStorage.clear();
		mockFetch.mockReset();

		// ローカルストレージのモックを設定
		Object.defineProperty(window, "localStorage", {
			value: mockLocalStorage,
			writable: true,
		});

		// process.env のモック
		vi.stubEnv("NEXT_PUBLIC_BACKEND_HOST", "http://localhost:3000");
	});

	afterEach(() => {
		vi.unstubAllEnvs();
	});

	it("キャッシュデータが利用可能な場合、それを使用して初期化される", () => {
		// キャッシュデータを設定
		mockLocalStorage.setItem(
			"cached_multi_choice_question",
			JSON.stringify(mockExercise),
		);
		mockLocalStorage.setItem("multi_choice_generation_status", "completed");

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		expect(result.current.exercise).toEqual(mockExercise);
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBe("");
	});

	it("キャッシュデータが存在しない場合、新しい問題を生成する", async () => {
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockExercise),
		});

		mockLocalStorage.setItem("selectedFiles", JSON.stringify(["file1.pdf"]));
		mockLocalStorage.setItem("title", "Test Title");

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.exercise).toEqual(mockExercise);
		expect(mockFetch).toHaveBeenCalledTimes(1);
		expect(mockFetch).toHaveBeenCalledWith(
			"http://localhost:3000/exercises/multiple_choice",
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					files: ["file1.pdf"],
					title: "Test Title",
				}),
			},
		);
	});

	it("フェッチのエラーを適切に処理する", async () => {
		// 必要なデータを設定
		mockLocalStorage.setItem("selectedFiles", JSON.stringify(["file1.pdf"]));
		mockLocalStorage.setItem("title", "Test Title");

		const mockError = new Error("API Error");
		mockFetch.mockRejectedValueOnce(mockError);

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe(mockError.message);
	});

	it("キャッシュを正しくクリアする", async () => {
		mockLocalStorage.setItem(
			"cached_multi_choice_question",
			JSON.stringify(mockExercise),
		);
		mockLocalStorage.setItem("multi_choice_generation_status", "completed");

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		await act(async () => {
			result.current.clearCache();
		});

		expect(mockLocalStorage.getItem("cached_multi_choice_question")).toBeNull();
		expect(
			mockLocalStorage.getItem("multi_choice_generation_status"),
		).toBeNull();
	});

	it("問題を正しくリセットする", async () => {
		// 初期データを設定
		mockLocalStorage.setItem(
			"cached_multi_choice_question",
			JSON.stringify(mockExercise),
		);
		mockLocalStorage.setItem("multi_choice_generation_status", "completed");

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		// 初期状態を確認
		expect(result.current.exercise).toEqual(mockExercise);

		// resetExerciseを実行
		await act(async () => {
			result.current.resetExercise();
		});

		// ローカルストレージがクリアされていることを確認
		expect(mockLocalStorage.getItem("cached_multi_choice_question")).toBeNull();
		expect(
			mockLocalStorage.getItem("multi_choice_generation_status"),
		).toBeNull();

		// exerciseとparsedResponseがnullに設定されていることを確認
		expect(result.current.exercise).toBeNull();
		expect(result.current.parsedResponse).toBeNull();
	});

	it("IDが提供された場合、特定の問題をフェッチする", async () => {
		const exerciseId = "123";
		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockExercise),
		});

		const { result } = renderHook(() => useGetMultiChoiceQuestion(exerciseId));

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(mockFetch).toHaveBeenCalledWith(
			`http://localhost:3000/exercises/${exerciseId}`,
			{ method: "GET" },
		);
		expect(result.current.exercise).toEqual(mockExercise);
	});

	it("問題レスポンスの無効なJSONを適切に処理する", async () => {
		// 必要なデータを設定
		mockLocalStorage.setItem("selectedFiles", JSON.stringify(["file1.pdf"]));
		mockLocalStorage.setItem("title", "Test Title");

		const invalidExercise = {
			...mockExercise,
			response: "invalid json",
		};

		mockFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(invalidExercise),
		});

		const { result } = renderHook(() => useGetMultiChoiceQuestion());

		await waitFor(() => {
			expect(result.current.error).toBe("問題データの解析に失敗しました");
		});
	});
});
