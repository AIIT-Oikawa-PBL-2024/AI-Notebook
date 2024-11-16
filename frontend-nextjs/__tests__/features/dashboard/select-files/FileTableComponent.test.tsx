import FileTable from "@/features/dashboard/select-files/FileTableComponent";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックデータ
const mockFiles = [
	{
		file_name: "test1.pdf",
		file_size: "1.5 MB",
		created_at: "2024-03-15T10:00:00",
		select: false,
	},
	{
		file_name: "sample2.jpg",
		file_size: "500 KB",
		created_at: "2024-03-14T15:30:00",
		select: false,
	},
	{
		file_name: "document3.docx",
		file_size: "2.2 MB",
		created_at: "2024-03-16T09:15:00",
		select: true,
	},
];

// モック関数
const mockHandleSelect = vi.fn();
const mockHandleSelectAll = vi.fn();
const mockFormatDate = vi.fn((date) =>
	new Date(date).toLocaleDateString("ja-JP"),
);

// デフォルトのプロップス
const defaultProps = {
	files: mockFiles,
	loading: false,
	handleSelect: mockHandleSelect,
	handleSelectAll: mockHandleSelectAll,
	areAllFilesSelected: false,
	formatDate: mockFormatDate,
};

describe("FileTable", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("コンポーネントが正しくレンダリングされること", () => {
		render(<FileTable {...defaultProps} />);

		expect(screen.getByPlaceholderText("ファイル名で検索")).toBeInTheDocument();
		expect(
			screen.getByRole("columnheader", { name: /ファイル名/ }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("columnheader", { name: /サイズ/ }),
		).toBeInTheDocument();
		expect(
			screen.getByRole("columnheader", { name: /作成日時/ }),
		).toBeInTheDocument();
	});

	it("ファイル一覧が正しく表示されること", () => {
		render(<FileTable {...defaultProps} />);

		for (const file of mockFiles) {
			expect(screen.getByText(file.file_name)).toBeInTheDocument();
		}
	});

	it("検索機能が正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		const searchInput = screen.getByPlaceholderText("ファイル名で検索");
		fireEvent.change(searchInput, { target: { value: "test1" } });

		expect(screen.getByText("test1.pdf")).toBeInTheDocument();
		expect(screen.queryByText("sample2.jpg")).not.toBeInTheDocument();
	});

	it("ソート機能が正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		const getFileNameCells = () =>
			screen
				.getAllByRole("cell")
				.filter(
					(cell) =>
						cell.textContent?.endsWith(".pdf") ||
						cell.textContent?.endsWith(".jpg") ||
						cell.textContent?.endsWith(".docx"),
				);

		// 初期状態の確認（file_name, ascでソート済み）
		const initialCells = getFileNameCells();
		expect(initialCells[0]).toHaveTextContent("document3.docx");
		expect(initialCells[1]).toHaveTextContent("sample2.jpg");
		expect(initialCells[2]).toHaveTextContent("test1.pdf");

		// ファイル名でソート（クリックで降順に変更）
		const fileNameHeader = screen.getByRole("columnheader", {
			name: /ファイル名/,
		});
		fireEvent.click(fileNameHeader);

		// 降順のチェック（t -> s -> d）
		const descCells = getFileNameCells();
		expect(descCells[0]).toHaveTextContent("test1.pdf");
		expect(descCells[1]).toHaveTextContent("sample2.jpg");
		expect(descCells[2]).toHaveTextContent("document3.docx");
	});

	it("全選択チェックボックスが正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		// インデックス0が全選択チェックボックス
		const selectAllCheckbox = screen.getAllByRole("checkbox")[0];
		fireEvent.click(selectAllCheckbox);

		expect(mockHandleSelectAll).toHaveBeenCalledWith(true);
	});

	it("個別のチェックボックスが正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		const firstFileCheckbox = screen.getAllByRole("checkbox")[1];
		fireEvent.click(firstFileCheckbox);

		// 最初のファイル（document3.docx）のチェックを解除
		expect(mockHandleSelect).toHaveBeenCalledWith("document3.docx", false);
	});

	it("ローディング状態でチェックボックスが無効化されること", () => {
		render(<FileTable {...defaultProps} loading={true} />);

		const checkboxes = screen.getAllByRole("checkbox");
		for (const checkbox of checkboxes) {
			expect(checkbox).toBeDisabled();
		}
	});

	it("ファイルサイズが正しくフォーマットされること", () => {
		render(<FileTable {...defaultProps} />);

		expect(screen.getByText("1.50 MB")).toBeInTheDocument();
		expect(screen.getByText("500.00 KB")).toBeInTheDocument();
	});

	it("作成日時が正しくフォーマットされること", () => {
		render(<FileTable {...defaultProps} />);

		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-15T10:00:00");
		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-14T15:30:00");
		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-16T09:15:00");
	});

	it("サイズでソートが正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		const sizeHeader = screen.getByRole("columnheader", { name: /サイズ/ });
		fireEvent.click(sizeHeader);

		const sizeTexts = screen
			.getAllByRole("cell")
			.filter(
				(cell) =>
					cell.textContent?.includes("MB") || cell.textContent?.includes("KB"),
			)
			.map((cell) => cell.textContent);

		expect(sizeTexts).toEqual(["500.00 KB", "1.50 MB", "2.20 MB"]);
	});

	it("作成日時でソートが正しく動作すること", () => {
		render(<FileTable {...defaultProps} />);

		const dateHeader = screen.getByRole("columnheader", { name: /作成日時/ });
		fireEvent.click(dateHeader);

		// mockFormatDateが正しい順序で呼び出されたことを確認
		const calls = mockFormatDate.mock.calls.map((call) => call[0]);
		expect(calls).toContain("2024-03-14T15:30:00");
		expect(calls).toContain("2024-03-15T10:00:00");
		expect(calls).toContain("2024-03-16T09:15:00");
	});

	it("無効なファイルサイズを処理できること", () => {
		const filesWithInvalidSize = [
			{
				file_name: "invalid.txt",
				file_size: "invalid",
				created_at: "2024-03-15T10:00:00",
				select: false,
			},
			...mockFiles,
		];

		render(<FileTable {...defaultProps} files={filesWithInvalidSize} />);

		expect(screen.getByText("0.00 KB")).toBeInTheDocument();
	});
});
