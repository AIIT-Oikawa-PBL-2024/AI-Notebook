import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import FileUploadComponent from "@/features/dashboard/fileupload/FileUpload";
import { useFileUpload } from "@/features/dashboard/fileupload/hooks/useFileUpload";
import { vi, type Mock, beforeEach, describe, expect, it } from "vitest";

// Mock the custom hook
vi.mock("@/hooks/useFileUpload", () => ({
	useFileUpload: vi.fn(),
}));

describe("FileUploadComponent", () => {
	const mockUploadFiles = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
		(useFileUpload as Mock).mockReturnValue({
			uploadFiles: mockUploadFiles,
			isUploading: false,
		});
	});

	it("renders upload area with correct text", () => {
		render(<FileUploadComponent />);
		expect(
			screen.getByText(
				"PDF、PNG、JPEGファイルをドラッグ＆ドロップするか、クリックして選択してください",
			),
		).toBeInTheDocument();
	});

	it("handles file selection through input", async () => {
		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });

		await waitFor(() => {
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
			expect(screen.getByText("(4 bytes)")).toBeInTheDocument();
		});
	});

	it("shows error message for invalid file type", async () => {
		render(<FileUploadComponent />);
		const file = new File(["test"], "test.txt", { type: "text/plain" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });

		await waitFor(() => {
			expect(
				screen.getByText(
					"test.txt は許可されていないファイル形式です。PDF、PNG、JPEGファイルのみアップロード可能です。",
				),
			).toBeInTheDocument();
		});
	});

	it("handles file removal", async () => {
		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });
		await waitFor(() => {
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
		});

		const removeButton = screen.getByTitle("Remove file icon");
		fireEvent.click(removeButton);

		await waitFor(() => {
			expect(screen.queryByText("test.pdf")).not.toBeInTheDocument();
		});
	});

	it("handles successful file upload", async () => {
		const mockAlert = vi.spyOn(window, "alert").mockImplementation(() => {});
		mockUploadFiles.mockResolvedValueOnce(true);

		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });
		await waitFor(() => {
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
		});

		const uploadButton = screen.getByText("アップロード");
		fireEvent.click(uploadButton);

		await waitFor(() => {
			expect(mockUploadFiles).toHaveBeenCalled();
			expect(mockAlert).toHaveBeenCalledWith(
				"ファイルが正常にアップロードされました",
			);
			expect(screen.queryByText("test.pdf")).not.toBeInTheDocument();
		});

		mockAlert.mockRestore();
	});

	it("handles upload failure", async () => {
		const mockAlert = vi.spyOn(window, "alert").mockImplementation(() => {});
		mockUploadFiles.mockRejectedValueOnce(new Error("Upload failed"));

		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });
		await waitFor(() => {
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
		});

		const uploadButton = screen.getByText("アップロード");
		fireEvent.click(uploadButton);

		await waitFor(() => {
			expect(mockUploadFiles).toHaveBeenCalled();
			expect(mockAlert).toHaveBeenCalledWith("エラー: Upload failed");
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
		});

		mockAlert.mockRestore();
	});

	it("handles drag and drop", async () => {
		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const dropArea = screen.getByText(
			"PDF、PNG、JPEGファイルをドラッグ＆ドロップするか、クリックして選択してください",
		).parentElement;

		if (!dropArea) {
			throw new Error("Drop area not found");
		}

		// Test dragenter
		fireEvent.dragEnter(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});
		expect(dropArea).toHaveClass("border-blue-400");

		// Test drop
		fireEvent.drop(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});

		await waitFor(() => {
			expect(screen.getByText("test.pdf")).toBeInTheDocument();
			expect(dropArea).not.toHaveClass("border-blue-400");
		});
	});

	it("shows loading state during upload", async () => {
		(useFileUpload as Mock).mockReturnValue({
			uploadFiles: mockUploadFiles,
			isUploading: true,
		});

		render(<FileUploadComponent />);
		const file = new File(["test"], "test.pdf", { type: "application/pdf" });
		const input = screen.getByRole("file");

		fireEvent.change(input, { target: { files: [file] } });
		await waitFor(() => {
			expect(screen.getByText("アップロード中...")).toBeInTheDocument();
			expect(screen.getByText("アップロード中...")).toBeDisabled();
		});
	});
});
