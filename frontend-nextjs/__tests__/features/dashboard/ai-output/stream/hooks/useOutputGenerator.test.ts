import { useOutputGenerator } from "@/features/dashboard/ai-output/stream/hooks/useOutputGenerator";
import * as useAuthFetchModule from "@/hooks/useAuthFetch";
import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Mock the ReadableStream
class MockReadableStream {
	private chunks: string[];
	private currentIndex: number;

	constructor(chunks: string[]) {
		this.chunks = chunks;
		this.currentIndex = 0;
	}

	getReader() {
		return {
			read: async () => {
				if (this.currentIndex >= this.chunks.length) {
					return { done: true, value: undefined };
				}
				const chunk = this.chunks[this.currentIndex];
				this.currentIndex++;
				return {
					done: false,
					value: new TextEncoder().encode(chunk),
				};
			},
		};
	}
}

describe("useOutputGenerator", () => {
	const mockAuthFetch = vi.fn();
	const mockLocalStorageData = {
		selectedFiles: JSON.stringify(["file1.pdf", "file2.pdf"]),
		title: "テストタイトル",
	};

	beforeEach(() => {
		// Mock localStorage
		vi.spyOn(Storage.prototype, "getItem").mockImplementation(
			(key) =>
				mockLocalStorageData[key as keyof typeof mockLocalStorageData] || null,
		);

		// Mock useAuthFetch
		vi.spyOn(useAuthFetchModule, "useAuthFetch").mockReturnValue(mockAuthFetch);
	});

	afterEach(() => {
		vi.clearAllMocks();
	});

	it("正常系: ストリーミングデータを正しく処理できること", async () => {
		const mockStreamChunks = ["チャンク1", "チャンク2", "チャンク3"];
		const mockResponse = {
			ok: true,
			body: new MockReadableStream(mockStreamChunks),
		};
		mockAuthFetch.mockResolvedValue(mockResponse);

		const { result } = renderHook(() => useOutputGenerator());

		// 初期状態の確認
		expect(result.current.loading).toBe(true);
		expect(result.current.error).toBe("");
		expect(result.current.output).toBe("");

		// ストリーミングが完了するまで待機
		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		// 最終状態の確認
		expect(result.current.output).toBe("チャンク1チャンク2チャンク3");
		expect(result.current.error).toBe("");

		// APIコールの検証
		expect(mockAuthFetch).toHaveBeenCalledWith(
			`${process.env.NEXT_PUBLIC_BACKEND_HOST}/outputs/request_stream`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					files: ["file1.pdf", "file2.pdf"],
					title: "テストタイトル",
				}),
			},
		);
	});

	it("エラー系: localStorage に必要なデータがない場合", async () => {
		vi.spyOn(Storage.prototype, "getItem").mockReturnValue(null);

		const { result } = renderHook(() => useOutputGenerator());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("必要な情報が見つかりません");
		expect(mockAuthFetch).not.toHaveBeenCalled();
	});

	it("エラー系: APIレスポンスが失敗の場合", async () => {
		mockAuthFetch.mockResolvedValue({ ok: false });

		const { result } = renderHook(() => useOutputGenerator());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("AI要約の生成に失敗しました");
	});

	it("エラー系: ストリーミングの初期化に失敗する場合", async () => {
		mockAuthFetch.mockResolvedValue({
			ok: true,
			body: null,
		});

		const { result } = renderHook(() => useOutputGenerator());

		await waitFor(() => {
			expect(result.current.loading).toBe(false);
		});

		expect(result.current.error).toBe("ストリーミングの初期化に失敗しました");
	});
});
