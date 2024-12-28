import { useDeleteAnswers } from "@/features/dashboard/ai-exercise/select-answers/useDeleteAnswers";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

describe("useDeleteAnswers", () => {
	const mockAuthFetch = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("回答を正常に削除できること", async () => {
		const mockResponse = {
			ok: true,
			json: vi.fn().mockResolvedValue({
				deleted_ids: [1, 2],
				not_found_ids: [],
				unauthorized_ids: [],
			}),
		};

		mockAuthFetch.mockResolvedValue(mockResponse);

		const { result } = renderHook(() => useDeleteAnswers());

		let response!: {
			deleted_ids: number[];
			not_found_ids: number[];
			unauthorized_ids: number[];
		};
		await act(async () => {
			response = await result.current.deleteAnswers([1, 2]);
		});

		// APIエンドポイントとリクエストオプションが正しいことを確認
		expect(mockAuthFetch).toHaveBeenCalledWith(
			expect.stringContaining("/answers/bulk_delete"),
			expect.objectContaining({
				method: "DELETE",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({ answer_ids: [1, 2] }),
			}),
		);

		// 正常なレスポンスを確認
		expect(response).toEqual({
			deleted_ids: [1, 2],
			not_found_ids: [],
			unauthorized_ids: [],
		});

		// エラーメッセージが空であることを確認
		expect(result.current.error).toBe("");
		// ローディングがfalseになっていることを確認
		expect(result.current.loading).toBe(false);
	});

	it("サーバーエラーが発生した場合に正しく処理されること", async () => {
		const mockResponse = {
			ok: false,
			json: vi.fn().mockResolvedValue({}),
		};

		mockAuthFetch.mockResolvedValue(mockResponse);

		const { result } = renderHook(() => useDeleteAnswers());

		await act(async () => {
			await expect(result.current.deleteAnswers([1, 2])).rejects.toThrow(
				"回答の一括削除に失敗しました。",
			);
		});

		// エラーメッセージが正しく設定されることを確認
		expect(result.current.error).toBe("回答の一括削除に失敗しました。");
		// ローディングがfalseになっていることを確認
		expect(result.current.loading).toBe(false);
	});

	it("ネットワークエラーが発生した場合に正しく処理されること", async () => {
		mockAuthFetch.mockRejectedValue(new Error("Network Error"));

		const { result } = renderHook(() => useDeleteAnswers());

		await act(async () => {
			await expect(result.current.deleteAnswers([1, 2])).rejects.toThrow(
				"Network Error",
			);
		});

		// エラーメッセージが正しく設定されることを確認
		expect(result.current.error).toBe("Network Error");
		// ローディングがfalseになっていることを確認
		expect(result.current.loading).toBe(false);
	});
});
