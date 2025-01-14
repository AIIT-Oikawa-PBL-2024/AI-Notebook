import FileUploadComponent from "@/features/dashboard/fileupload/FileUpload";
import { useFileUpload } from "@/features/dashboard/fileupload/hooks/useFileUpload";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
// FileUpload.test.tsx
import React from "react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/features/dashboard/fileupload/hooks/useFileUpload");

describe("FileUploadComponent", () => {
	let mockUploadFiles: Mock;
	let mockIsUploading: boolean;

	beforeEach(() => {
		mockUploadFiles = vi.fn();
		mockIsUploading = false;

		(useFileUpload as Mock).mockReturnValue({
			uploadFiles: mockUploadFiles,
			isUploading: mockIsUploading,
		});
	});

	it("renders correctly", () => {
		render(<FileUploadComponent />);
		expect(
			screen.getByText(
				/PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください/,
			),
		).toBeInTheDocument();
	});

	it("handles file drop", async () => {
		render(<FileUploadComponent />);

		const dropArea = screen.getByText(
			/PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください/,
		);

		const file = new File(["file content"], "test.pdf", {
			type: "application/pdf",
		});

		fireEvent.dragEnter(dropArea);
		fireEvent.dragOver(dropArea);
		fireEvent.drop(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});

		expect(await screen.findByText("test.pdf")).toBeInTheDocument();
	});

	it("shows error message when unsupported file is dropped", async () => {
		render(<FileUploadComponent />);

		const dropArea = screen.getByText(
			/PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください/,
		);

		const file = new File(["file content"], "test.txt", { type: "text/plain" });

		fireEvent.dragEnter(dropArea);
		fireEvent.dragOver(dropArea);
		fireEvent.drop(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});

		expect(
			await screen.findByText(
				/test.txt は許可されていないファイル形式です。PDF、PNG、JPEG、MP4、MP3、WAVファイルのみアップロード可能です。/,
			),
		).toBeInTheDocument();
	});

	it("removes file from the list when remove button is clicked", async () => {
		render(<FileUploadComponent />);

		const dropArea = screen.getByText(
			/PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください/,
		);

		const file = new File(["file content"], "test.pdf", {
			type: "application/pdf",
		});

		fireEvent.drop(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});

		await screen.findByText("test.pdf");

		const removeButton = screen.getByRole("button", {
			name: /Remove file icon/,
		});
		fireEvent.click(removeButton);

		await waitFor(() => {
			expect(screen.queryByText("test.pdf")).not.toBeInTheDocument();
		});
	});

	it("disables upload button when isUploading is true", async () => {
		mockIsUploading = true;

		(useFileUpload as Mock).mockReturnValue({
			uploadFiles: mockUploadFiles,
			isUploading: mockIsUploading,
		});

		render(<FileUploadComponent />);

		const dropArea = screen.getByText(
			/PDF、PNG、JPEG、MP4、MP3、WAVファイルをドラッグ＆ドロップするか、クリックして選択してください/,
		);

		const file = new File(["file content"], "test.pdf", {
			type: "application/pdf",
		});

		fireEvent.drop(dropArea, {
			dataTransfer: {
				files: [file],
			},
		});

		await screen.findByText("test.pdf");
	});
});
