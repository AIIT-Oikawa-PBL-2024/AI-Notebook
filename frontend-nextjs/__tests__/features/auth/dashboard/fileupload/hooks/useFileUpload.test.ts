// useFileUpload.test.ts
import { renderHook, act } from "@testing-library/react";
import { useFileUpload } from "@/features/dashboard/fileupload/hooks/useFileUpload";
import { useAuth } from "@/providers/AuthProvider";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { vi, describe, it, expect, beforeEach, type Mock } from "vitest";

vi.mock("@/providers/AuthProvider");
vi.mock("@/hooks/useAuthFetch");

describe("useFileUpload", () => {
	let mockUser: { uid: string };
	let mockAuthFetch: Mock;

	beforeEach(() => {
		mockUser = { uid: "test-uid" };
		(useAuth as Mock).mockReturnValue({ user: mockUser });

		mockAuthFetch = vi.fn();
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("should upload files successfully", async () => {
		const { result } = renderHook(() => useFileUpload());

		const files = [
			{
				name: "test.pdf",
				size: 1234,
				type: "application/pdf",
				file: new File(["file content"], "test.pdf", {
					type: "application/pdf",
				}),
			},
		];

		// Mock the authFetch responses
		mockAuthFetch
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({
					"test-uid/test.pdf": "https://signedurl.com/test.pdf",
				}),
			})
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({ success: true }),
			});

		// Mock the fetch call to the signed URL (uploading the file)
		global.fetch = vi.fn().mockResolvedValueOnce({
			ok: true,
		});

		await act(async () => {
			const success = await result.current.uploadFiles(files);
			expect(success).toBe(true);
		});

		expect(result.current.isUploading).toBe(false);
		expect(mockAuthFetch).toHaveBeenCalledTimes(2);
		expect(global.fetch).toHaveBeenCalledTimes(1);
	});

	it("should handle failure to get signed URLs", async () => {
		const { result } = renderHook(() => useFileUpload());

		const files = [
			{
				name: "test.pdf",
				size: 1234,
				type: "application/pdf",
				file: new File(["file content"], "test.pdf", {
					type: "application/pdf",
				}),
			},
		];

		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
			status: 500,
		});

		await act(async () => {
			await expect(result.current.uploadFiles(files)).rejects.toThrow(
				"Failed to get signed URLs",
			);
		});

		expect(result.current.isUploading).toBe(false);
		expect(mockAuthFetch).toHaveBeenCalledTimes(1);
	});

	it("should handle failure to upload file", async () => {
		const { result } = renderHook(() => useFileUpload());

		const files = [
			{
				name: "test.pdf",
				size: 1234,
				type: "application/pdf",
				file: new File(["file content"], "test.pdf", {
					type: "application/pdf",
				}),
			},
		];

		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: async () => ({
				"test-uid/test.pdf": "https://signedurl.com/test.pdf",
			}),
		});

		global.fetch = vi.fn().mockResolvedValueOnce({
			ok: false,
			status: 500,
		});

		await act(async () => {
			await expect(result.current.uploadFiles(files)).rejects.toThrow(
				"Failed to upload file",
			);
		});

		expect(result.current.isUploading).toBe(false);
		expect(mockAuthFetch).toHaveBeenCalledTimes(1);
		expect(global.fetch).toHaveBeenCalledTimes(1);
	});

	it("should handle failure to register file", async () => {
		const { result } = renderHook(() => useFileUpload());

		const files = [
			{
				name: "test.pdf",
				size: 1234,
				type: "application/pdf",
				file: new File(["file content"], "test.pdf", {
					type: "application/pdf",
				}),
			},
		];

		mockAuthFetch
			.mockResolvedValueOnce({
				ok: true,
				json: async () => ({
					"test-uid/test.pdf": "https://signedurl.com/test.pdf",
				}),
			})
			.mockResolvedValueOnce({
				ok: false,
				status: 500,
			});

		global.fetch = vi.fn().mockResolvedValueOnce({
			ok: true,
		});

		await act(async () => {
			await expect(result.current.uploadFiles(files)).rejects.toThrow(
				"Failed to register file",
			);
		});

		expect(result.current.isUploading).toBe(false);
		expect(mockAuthFetch).toHaveBeenCalledTimes(2);
		expect(global.fetch).toHaveBeenCalledTimes(1);
	});
});
