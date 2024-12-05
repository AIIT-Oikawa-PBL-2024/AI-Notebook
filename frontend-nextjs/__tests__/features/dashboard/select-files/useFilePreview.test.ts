import { useFilePreview } from "@/features/dashboard/select-files/useFilePreview";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { act, renderHook } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

describe("useFilePreview", () => {
	const mockAuthFetch = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("初期状態で空のステートが設定されていること", () => {
		const { result } = renderHook(() => useFilePreview());

		expect(result.current.previewUrls).toEqual({});
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
	});

	it("プレビューURLが正常に生成されること", async () => {
		const mockResponse = {
			"path/to/file1.pdf": "http://example.com/signed-url-1",
			"path/to/file2.jpg": "http://example.com/signed-url-2",
		};

		mockAuthFetch.mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockResponse),
		});

		const { result } = renderHook(() => useFilePreview());

		await act(async () => {
			await result.current.generatePreviewUrl(["file1.pdf", "file2.jpg"]);
		});

		expect(mockAuthFetch).toHaveBeenCalledWith(
			expect.stringContaining("/files/generate_download_signed_url"),
			expect.objectContaining({
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(["file1.pdf", "file2.jpg"]),
			}),
		);

		expect(result.current.previewUrls).toEqual({
			"file1.pdf": {
				fileName: "file1.pdf",
				url: "http://example.com/signed-url-1",
				contentType: "application/pdf",
			},
			"file2.jpg": {
				fileName: "file2.jpg",
				url: "http://example.com/signed-url-2",
				contentType: "image/jpeg",
			},
		});
		expect(result.current.loading).toBe(false);
		expect(result.current.error).toBeNull();
	});

	it("APIエラーが適切にハンドリングされること", async () => {
		mockAuthFetch.mockResolvedValue({
			ok: false,
			json: () =>
				Promise.resolve({ message: "署名付きURLの生成に失敗しました" }),
		});

		const { result } = renderHook(() => useFilePreview());

		await act(async () => {
			await result.current.generatePreviewUrl(["file1.pdf"]);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe("署名付きURLの生成に失敗しました");
		});
		expect(result.current.loading).toBe(false);
		expect(result.current.previewUrls).toEqual({});
	});

	it("ネットワークエラーが適切にハンドリングされること", async () => {
		const mockError = new Error("Network Error");
		mockAuthFetch.mockRejectedValue(mockError);

		const { result } = renderHook(() => useFilePreview());

		await act(async () => {
			await result.current.generatePreviewUrl(["file1.pdf"]);
		});

		await vi.waitFor(() => {
			expect(result.current.error).toBe("Network Error");
		});
		expect(result.current.loading).toBe(false);
		expect(result.current.previewUrls).toEqual({});
	});

	it("プレビューのクリア機能が正常に動作すること", () => {
		const { result } = renderHook(() => useFilePreview());

		act(() => {
			result.current.clearPreviews();
		});

		expect(result.current.previewUrls).toEqual({});
		expect(result.current.error).toBeNull();
	});

	it("様々なファイルタイプが正しく処理されること", async () => {
		const mockResponse = {
			"path/to/file.pdf": "http://example.com/pdf",
			"path/to/file.png": "http://example.com/png",
			"path/to/file.jpg": "http://example.com/jpg",
			"path/to/file.mp4": "http://example.com/mp4",
			"path/to/file.mp3": "http://example.com/mp3",
			"path/to/file.wav": "http://example.com/wav",
			"path/to/file.unknown": "http://example.com/unknown",
		};

		mockAuthFetch.mockResolvedValue({
			ok: true,
			json: () => Promise.resolve(mockResponse),
		});

		const { result } = renderHook(() => useFilePreview());

		await act(async () => {
			await result.current.generatePreviewUrl([
				"file.pdf",
				"file.png",
				"file.jpg",
				"file.mp4",
				"file.mp3",
				"file.wav",
				"file.unknown",
			]);
		});

		expect(result.current.previewUrls).toMatchObject({
			"file.pdf": { contentType: "application/pdf" },
			"file.png": { contentType: "image/png" },
			"file.jpg": { contentType: "image/jpeg" },
			"file.mp4": { contentType: "video/mp4" },
			"file.mp3": { contentType: "audio/mpeg" },
			"file.wav": { contentType: "audio/wav" },
			"file.unknown": { contentType: "application/octet-stream" },
		});
	});
});
