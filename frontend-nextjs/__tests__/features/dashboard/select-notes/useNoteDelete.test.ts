import { useNoteDelete } from "@/features/dashboard/select-notes/useNoteDelete";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { act, renderHook } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モックの設定
vi.mock("next/navigation", () => ({
	useRouter: vi.fn(),
}));

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

describe("useNoteDelete", () => {
	const mockAuthFetch = vi.fn();
	const mockRouter = { refresh: vi.fn() };
	const mockOnSuccess = vi.fn().mockImplementation(() => Promise.resolve());
	const mockOnError = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		// useAuthFetchのモックを更新
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
		// useRouterのモックを更新
		(useRouter as Mock).mockReturnValue(mockRouter);
	});

	it("ノートの削除が成功した場合の処理が正しく動作すること", async () => {
		// APIレスポンスのモックを設定
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
		});

		const { result } = renderHook(() =>
			useNoteDelete({
				onSuccess: mockOnSuccess,
				onError: mockOnError,
			}),
		);

		await act(async () => {
			await result.current.deleteNote(1);
		});

		// 非同期処理の完了を待つ
		await vi.waitFor(() => {
			expect(result.current.error).toBeNull();
		});

		// 正しいURLとオプションでAPIが呼ばれたことを確認
		expect(mockAuthFetch).toHaveBeenCalledWith(
			`${process.env.NEXT_PUBLIC_BACKEND_HOST}/notes/1`,
			{
				method: "DELETE",
				headers: {
					"Content-Type": "application/json",
				},
			},
		);

		// 成功時の処理が正しく実行されたことを確認
		expect(mockOnSuccess).toHaveBeenCalled();
		expect(mockRouter.refresh).toHaveBeenCalled();
		expect(result.current.isDeleting).toBe(false);
	});

	it("APIエラーレスポンスの処理が正しく動作すること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
			status: 404,
			json: () => Promise.resolve({ detail: "ノートが見つかりません。" }),
		});

		const { result } = renderHook(() =>
			useNoteDelete({ onError: mockOnError }),
		);

		await act(async () => {
			await result.current.deleteNote(1);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe("ノートが見つかりません。");
		});

		expect(mockOnError).toHaveBeenCalledWith("ノートが見つかりません。");
		expect(result.current.isDeleting).toBe(false);
	});

	it("noteIdが不正な場合のエラー処理が正しく動作すること", async () => {
		const { result } = renderHook(() =>
			useNoteDelete({ onError: mockOnError }),
		);

		await act(async () => {
			await result.current.deleteNote(0);
		});

		// 不正なnoteIdのエラーハンドリングの確認
		expect(mockOnError).toHaveBeenCalledWith(
			"削除するノートが選択されていません。",
		);
		expect(result.current.error).toBe("削除するノートが選択されていません。");
		expect(result.current.isDeleting).toBe(false);
		expect(mockAuthFetch).not.toHaveBeenCalled();
	});

	it("予期せぬエラーが発生した場合の処理が正しく動作すること", async () => {
		// 非Error型のエラーをスローする
		mockAuthFetch.mockRejectedValueOnce("Unknown error");

		const { result } = renderHook(() =>
			useNoteDelete({ onError: mockOnError }),
		);

		await act(async () => {
			await result.current.deleteNote(1);
		});

		expect(result.current.error).toBe("予期せぬエラーが発生しました。");
		expect(mockOnError).toHaveBeenCalledWith("予期せぬエラーが発生しました。");
		expect(result.current.isDeleting).toBe(false);
	});

	it("削除処理中のisDeleting状態が正しく更新されること", async () => {
		// 非同期処理を模倣
		let resolvePromise: (value: { ok: boolean }) => void;
		const promise = new Promise<{ ok: boolean }>((resolve) => {
			resolvePromise = resolve;
		});

		mockAuthFetch.mockReturnValueOnce(promise);

		const { result } = renderHook(() => useNoteDelete());

		let deletePromise: Promise<void>;

		act(() => {
			deletePromise = result.current.deleteNote(1);
		});

		// 削除処理中のステータスを確認
		expect(result.current.isDeleting).toBe(true);

		// 非同期処理を完了
		await act(async () => {
			resolvePromise({ ok: true });
			await deletePromise;
		});

		// 削除処理完了後のステータスを確認
		expect(result.current.isDeleting).toBe(false);
	});
});
