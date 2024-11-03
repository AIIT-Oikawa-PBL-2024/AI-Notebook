import { renderHook, act } from "@testing-library/react";
import { useFileUpload } from "@/features/dashboard/fileupload/hooks/useFileUpload";
import { useAuth } from "@/providers/AuthProvider";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { vi, describe, it, expect, beforeEach } from "vitest";
import type { Mock } from "vitest";

// Mocking the hooks
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

describe("useFileUpload", () => {
	const mockUser = { uid: "test-user-id" };
	const mockAuthFetch = vi.fn();
	const mockFile = new File(["test"], "test.pdf", { type: "application/pdf" });
	const mockFileInfo = {
		name: "test.pdf",
		size: 4,
		type: "application/pdf",
		file: mockFile,
	};

	beforeEach(() => {
		vi.clearAllMocks();
		(useAuth as Mock).mockReturnValue({ user: mockUser });
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);
	});

	it("should throw error when user is not authenticated", async () => {
		(useAuth as Mock).mockReturnValue({ user: null });
		const { result } = renderHook(() => useFileUpload());

		await expect(result.current.uploadFiles([mockFileInfo])).rejects.toThrow(
			"User is not authenticated",
		);
	});

	it("should handle successful file upload", async () => {
		const mockSignedUrlResponse = {
			ok: true,
			json: () =>
				Promise.resolve({
					[`${mockUser.uid}/${mockFileInfo.name}`]: "signed-url",
				}),
		};
		const mockUploadResponse = { ok: true };
		const mockRegisterResponse = { ok: true };

		mockAuthFetch.mockResolvedValueOnce(mockSignedUrlResponse);
		global.fetch = vi.fn().mockResolvedValueOnce(mockUploadResponse);
		mockAuthFetch.mockResolvedValueOnce(mockRegisterResponse);

		const { result } = renderHook(() => useFileUpload());

		let success = false;
		await act(async () => {
			success = await result.current.uploadFiles([mockFileInfo]);
		});

		expect(success).toBe(true);
		expect(mockAuthFetch).toHaveBeenCalledTimes(2);
		expect(global.fetch).toHaveBeenCalledTimes(1);
	});

	it("should handle failed signed URL generation", async () => {
		const mockFailedResponse = { ok: false };
		mockAuthFetch.mockResolvedValueOnce(mockFailedResponse);

		const { result } = renderHook(() => useFileUpload());

		await expect(result.current.uploadFiles([mockFileInfo])).rejects.toThrow(
			"Failed to get signed URLs",
		);
	});

	it("should handle failed file upload", async () => {
		const mockSignedUrlResponse = {
			ok: true,
			json: () =>
				Promise.resolve({
					[`${mockUser.uid}/${mockFileInfo.name}`]: "signed-url",
				}),
		};
		const mockFailedUploadResponse = { ok: false };

		mockAuthFetch.mockResolvedValueOnce(mockSignedUrlResponse);
		global.fetch = vi.fn().mockResolvedValueOnce(mockFailedUploadResponse);

		const { result } = renderHook(() => useFileUpload());

		await expect(result.current.uploadFiles([mockFileInfo])).rejects.toThrow(
			"Failed to upload file",
		);
	});

	it("should handle failed file registration", async () => {
		const mockSignedUrlResponse = {
			ok: true,
			json: () =>
				Promise.resolve({
					[`${mockUser.uid}/${mockFileInfo.name}`]: "signed-url",
				}),
		};
		const mockUploadResponse = { ok: true };
		const mockFailedRegisterResponse = { ok: false };

		mockAuthFetch.mockResolvedValueOnce(mockSignedUrlResponse);
		global.fetch = vi.fn().mockResolvedValueOnce(mockUploadResponse);
		mockAuthFetch.mockResolvedValueOnce(mockFailedRegisterResponse);

		const { result } = renderHook(() => useFileUpload());

		await expect(result.current.uploadFiles([mockFileInfo])).rejects.toThrow(
			"Failed to register file",
		);
	});
});
