import { useFileDelete } from "@/features/dashboard/select-files/useFileDelete";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

const mockFiles = [
	{
		file_name: "test1.txt",
		file_size: "100KB",
		created_at: "2024-01-01",
		select: true,
	},
	{
		file_name: "test2.txt",
		file_size: "200KB",
		created_at: "2024-01-02",
		select: false,
	},
];

describe("useFileDelete", () => {
	const mockUser = { id: "1", name: "Test User" };
	const mockAuthFetch = vi.fn();
	const mockClearAuthError = vi.fn();
	const mockReAuthenticate = vi.fn();
	const mockOnDeleteSuccess = vi
		.fn()
		.mockImplementation(() => Promise.resolve());

	beforeEach(() => {
		vi.clearAllMocks();

		(useAuth as Mock).mockReturnValue({
			user: mockUser,
			clearError: mockClearAuthError,
			reAuthenticate: mockReAuthenticate,
		});

		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("ファイルの削除が成功した場合の処理が正しく動作すること", async () => {
		// APIレスポンスのモックを設定
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve({ success: true }),
		});

		const { result } = renderHook(() => useFileDelete(mockOnDeleteSuccess));

		await act(async () => {
			await result.current.deleteSelectedFiles(mockFiles);
		});

		// 非同期処理の完了を待つ
		await vi.waitFor(() => {
			expect(result.current.success).toBe("選択したファイルを削除しました");
		});

		expect(mockAuthFetch).toHaveBeenCalledWith(
			expect.stringContaining("/files/delete_files"),
			expect.objectContaining({
				method: "DELETE",
				body: JSON.stringify(["test1.txt"]),
			}),
		);

		// モックの呼び出しを確認
		expect(mockClearAuthError).toHaveBeenCalled();
		expect(mockOnDeleteSuccess).toHaveBeenCalled();
	});

	it("認証エラーが発生した場合の処理が正しく動作すること", async () => {
		const mockError = new Error("Invalid token");
		mockAuthFetch.mockRejectedValueOnce(mockError);

		const { result } = renderHook(() => useFileDelete());

		await act(async () => {
			await result.current.deleteSelectedFiles(mockFiles);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe(mockError.message);
		});
		expect(mockReAuthenticate).toHaveBeenCalled();
	});

	it("ファイルが選択されていない場合のエラー処理が正しく動作すること", async () => {
		const { result } = renderHook(() => useFileDelete());

		await act(async () => {
			await result.current.deleteSelectedFiles([
				{ ...mockFiles[0], select: false },
				{ ...mockFiles[1], select: false },
			]);
		});

		expect(result.current.error).toBe("削除するファイルを選択してください");
		expect(mockAuthFetch).not.toHaveBeenCalled();
	});

	it("APIエラーレスポンスの処理が正しく動作すること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
			json: () => Promise.resolve({ message: "API error" }),
		});

		const { result } = renderHook(() => useFileDelete());

		await act(async () => {
			await result.current.deleteSelectedFiles(mockFiles);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe("API error");
		});
	});

	it("一部のファイル削除が失敗した場合の処理が正しく動作すること", async () => {
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () =>
				Promise.resolve({
					success: false,
					failed_files: ["test1.txt"],
				}),
		});

		const { result } = renderHook(() => useFileDelete());

		await act(async () => {
			await result.current.deleteSelectedFiles(mockFiles);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe("削除に失敗したファイル: test1.txt");
		});
	});

	it("成功メッセージのクリアが正しく動作すること", async () => {
		const { result } = renderHook(() => useFileDelete());

		act(() => {
			result.current.clearSuccess();
		});

		expect(result.current.success).toBe("");
	});

	it("エラーメッセージのクリアが正しく動作すること", async () => {
		const { result } = renderHook(() => useFileDelete());

		act(() => {
			result.current.clearError();
		});

		expect(result.current.error).toBe("");
	});

	it("未認証ユーザーの場合のエラー処理が正しく動作すること", async () => {
		(useAuth as Mock).mockReturnValue({
			user: null,
			clearError: mockClearAuthError,
			reAuthenticate: mockReAuthenticate,
		});

		const { result } = renderHook(() => useFileDelete());

		await act(async () => {
			await result.current.deleteSelectedFiles(mockFiles);
		});

		expect(result.current.error).toBe("認証が必要です");
		expect(mockAuthFetch).not.toHaveBeenCalled();
	});
});
