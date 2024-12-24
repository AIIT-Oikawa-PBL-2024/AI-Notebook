import { useSubmitAnswers } from "@/features/dashboard/ai-exercise/essay-question/useSubmitAnswers";
import { useAuthFetch } from "@/hooks/useAuthFetch";
// useSubmitAnswers.test.tsx
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// useAuthFetch をモック化する
vi.mock("@/hooks/useAuthFetch");

describe("useSubmitAnswers", () => {
	let mockAuthFetch: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		// モック関数の初期化
		mockAuthFetch = vi.fn();
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("正常に回答を送信できる場合", async () => {
		// モックのレスポンス
		const mockResponse = { ok: true, json: async () => ({ success: true }) };
		mockAuthFetch.mockResolvedValue(mockResponse);

		const { result } = renderHook(() => useSubmitAnswers());

		// 初期値のチェック
		expect(result.current.isSubmitting).toBe(false);
		expect(result.current.error).toBeNull();

		let submitPromise: Promise<unknown>;
		act(() => {
			// submitAnswers を呼び出し
			submitPromise = result.current.submitAnswers({ question: "answer" });
		});

		// 送信開始時は isSubmitting が true になる
		expect(result.current.isSubmitting).toBe(true);

		// 非同期処理が完了するのを待つ
		await act(async () => {
			const resultData = await submitPromise;
			// モックレスポンスの内容が返却されること
			expect(resultData).toEqual({ success: true });
		});

		// 送信完了後は isSubmitting が false に戻る
		expect(result.current.isSubmitting).toBe(false);
		// エラーは発生していない
		expect(result.current.error).toBeNull();

		// authFetch が正しい引数で呼ばれているかチェック
		expect(mockAuthFetch).toHaveBeenCalledWith(
			`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/user_answer`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ question: "answer" }),
			},
		);
	});

	it("エラー時にエラーメッセージがセットされる", async () => {
		// モックのレスポンス(エラー)
		const mockErrorResponse = { ok: false, statusText: "Bad Request" };
		mockAuthFetch.mockResolvedValue(mockErrorResponse);

		const { result } = renderHook(() => useSubmitAnswers());

		let submitPromise: Promise<unknown>;
		act(() => {
			submitPromise = result.current.submitAnswers({ question: "answer" });
		});

		// 送信開始時は isSubmitting が true になる
		expect(result.current.isSubmitting).toBe(true);

		await act(async () => {
			try {
				await submitPromise;
				// ここには到達しないはず
				throw new Error("Expected error was not thrown");
			} catch (err) {
				// 送信時にエラーが投げられる
				expect(err).toBeInstanceOf(Error);
				expect((err as Error).message).toBe("Error: Bad Request");
			}
		});

		// 送信完了後は isSubmitting が false に戻る
		expect(result.current.isSubmitting).toBe(false);
		// カスタムフック内の error ステートが更新される
		expect(result.current.error).toBe("Error: Bad Request");
	});
});
