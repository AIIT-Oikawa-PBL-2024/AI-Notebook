import { useEssayQuestionGenerator } from "@/features/dashboard/ai-exercise/essay-question/useEssayQuestionGenerator";
import { act, renderHook } from "@testing-library/react";
import {
	afterAll,
	afterEach,
	beforeAll,
	beforeEach,
	describe,
	expect,
	it,
	vi,
} from "vitest";

// モックの型定義
const mockAuthFetch = vi.fn();
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => mockAuthFetch,
}));

// テスト用のモックデータ
const mockExerciseResponse = {
	id: "1",
	content: [
		{
			id: "1",
			input: {
				questions: [
					{
						question_id: "1",
						question_text: "Test question?",
						answer: "Test answer",
						explanation: "Test explanation",
					},
				],
			},
			name: "Test Exercise",
			type: "multiple_choice",
		},
	],
};

// 警告を抑制
const originalConsoleError = console.error;
beforeAll(() => {
	console.error = vi.fn();
});

afterAll(() => {
	console.error = originalConsoleError;
});

describe("useEssayQuestionGenerator", () => {
	beforeEach(() => {
		localStorage.clear();
		vi.clearAllMocks();
		// 環境変数のモック
		process.env.NEXT_PUBLIC_BACKEND_HOST = "http://test-api";
		// 必要な情報を設定（デフォルトの状態）
		localStorage.setItem("selectedFiles", JSON.stringify(["file1.pdf"]));
		localStorage.setItem("title", "Test Title");
	});

	afterEach(() => {
		localStorage.clear();
	});

	it("初期状態ではloadingがtrueであること", async () => {
		mockAuthFetch.mockImplementationOnce(
			() => new Promise((resolve) => setTimeout(resolve, 100)),
		);
		const { result } = renderHook(() => useEssayQuestionGenerator());
		expect(result.current.loading).toBe(true);
	});

	it("ストレージされた問題が存在する場合はそれを使用すること", () => {
		localStorage.setItem(
			"cached_essay_question",
			JSON.stringify(mockExerciseResponse),
		);
		localStorage.setItem("essay_generation_status", "completed");

		const { result } = renderHook(() => useEssayQuestionGenerator());
		expect(result.current.exercise).toEqual(mockExerciseResponse);
	});

	it("問題生成が成功した場合、正しく状態が更新されること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockExerciseResponse,
		});

		const { result } = renderHook(() => useEssayQuestionGenerator());

		await vi.waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.exercise).toEqual(mockExerciseResponse);
		expect(result.current.error).toBe("");
		expect(localStorage.getItem("cached_essay_question")).toBe(
			JSON.stringify(mockExerciseResponse),
		);
		expect(localStorage.getItem("essay_generation_status")).toBe("completed");
	});

	it("API呼び出しが失敗した場合はエラーになること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
		});

		const { result } = renderHook(() => useEssayQuestionGenerator());

		await vi.waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("記述問題の生成に失敗しました");
	});

	it("resetExerciseが正しく動作すること", async () => {
		// 初期状態を設定
		localStorage.setItem(
			"cached_essay_question",
			JSON.stringify(mockExerciseResponse),
		);
		localStorage.setItem("essay_generation_status", "completed");

		// API呼び出しをモック
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockExerciseResponse,
		});

		const { result } = renderHook(() => useEssayQuestionGenerator());

		// resetExercise実行前に非同期処理が完了するのを待つ
		await vi.waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		act(() => {
			result.current.resetExercise();
		});

		expect(result.current.exercise).toBeNull();
		expect(result.current.loading).toBe(true);
		expect(localStorage.getItem("cached_essay_question")).toBeNull();
		expect(localStorage.getItem("essay_generation_status")).toBeNull();
	});

	it("clearCacheが正しく動作すること", async () => {
		// 初期状態を設定
		localStorage.setItem(
			"cached_essay_question",
			JSON.stringify(mockExerciseResponse),
		);
		localStorage.setItem("essay_generation_status", "completed");

		// API呼び出しをモック
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => mockExerciseResponse,
		});

		const { result } = renderHook(() => useEssayQuestionGenerator());

		// clearCache実行前に非同期処理が完了するのを待つ
		await vi.waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		act(() => {
			result.current.clearCache();
		});

		expect(result.current.exercise).toBeNull();
		expect(result.current.loading).toBe(true);
		expect(localStorage.getItem("cached_essay_question")).toBeNull();
		expect(localStorage.getItem("essay_generation_status")).toBeNull();
	});

	it("checkCacheが正しくストレージ状態を返すこと", () => {
		// 初期状態を設定
		localStorage.setItem(
			"cached_essay_question",
			JSON.stringify(mockExerciseResponse),
		);
		localStorage.setItem("essay_generation_status", "completed");

		const { result } = renderHook(() => useEssayQuestionGenerator());

		const cacheState = result.current.checkCache();

		expect(cacheState).toEqual({
			exercise: JSON.stringify(mockExerciseResponse),
			generationStatus: "completed",
		});
	});
});
