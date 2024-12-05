import FileTable from "@/features/dashboard/select-files/FileTableComponent";
import { AuthProvider } from "@/providers/AuthProvider";
import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// useFilePreview のモック
vi.mock("@/features/dashboard/select-files/useFilePreview", () => ({
	useFilePreview: () => ({
		previewUrls: {},
		generatePreviewUrl: vi.fn(),
	}),
}));

// Material Tailwind のモック
vi.mock("@material-tailwind/react", () => ({
	Card: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
	Checkbox: ({
		checked,
		onChange,
		disabled,
	}: {
		checked: boolean;
		onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
		disabled: boolean;
	}) => (
		<input
			type="checkbox"
			checked={checked}
			onChange={onChange}
			disabled={disabled}
			aria-checked={checked}
		/>
	),
	IconButton: ({
		children,
		onClick,
	}: {
		children: React.ReactNode;
		onClick: () => void;
	}) => (
		<button type="button" onClick={onClick}>
			{children}
		</button>
	),
	Typography: ({ children }: { children: React.ReactNode }) => (
		<span>{children}</span>
	),
}));

// AuthProvider のモック
vi.mock("@/providers/AuthProvider", () => ({
	AuthProvider: ({ children }: { children: React.ReactNode }) => (
		<>{children}</>
	),
}));

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

// テストコンポーネントをラップするヘルパー関数
const renderWithProviders = (component: React.ReactElement) => {
	return render(<AuthProvider>{component}</AuthProvider>);
};

describe("FileTable", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("コンポーネントが正しくレンダリングされること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
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
		renderWithProviders(<FileTable {...defaultProps} />);
		for (const file of mockFiles) {
			expect(screen.getByText(file.file_name)).toBeInTheDocument();
		}
	});

	it("検索機能が正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const searchInput = screen.getByPlaceholderText("ファイル名で検索");
		fireEvent.change(searchInput, { target: { value: "test1" } });

		expect(screen.getByText("test1.pdf")).toBeInTheDocument();
		expect(screen.queryByText("sample2.jpg")).not.toBeInTheDocument();
	});

	it("ソート機能が正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const fileNameHeader = screen.getByRole("columnheader", {
			name: /ファイル名/,
		});
		fireEvent.click(fileNameHeader);

		const cells = screen.getAllByRole("cell");
		const fileNameCells = cells.filter((cell) =>
			cell.textContent?.match(/\.(pdf|jpg|docx)$/),
		);

		// 昇順確認（文字列の自然な順序）
		expect(fileNameCells[0]).toHaveTextContent("test1.pdf");
		expect(fileNameCells[1]).toHaveTextContent("sample2.jpg");
		expect(fileNameCells[2]).toHaveTextContent("document3.docx");

		// もう一度クリックで降順に
		fireEvent.click(fileNameHeader);
		const sortedCells = screen
			.getAllByRole("cell")
			.filter((cell) => cell.textContent?.match(/\.(pdf|jpg|docx)$/));

		expect(sortedCells[0]).toHaveTextContent("document3.docx");
		expect(sortedCells[1]).toHaveTextContent("sample2.jpg");
		expect(sortedCells[2]).toHaveTextContent("test1.pdf");
	});

	it("全選択チェックボックスが正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const selectAllCheckbox = screen.getAllByRole("checkbox")[0];
		fireEvent.click(selectAllCheckbox);
		expect(mockHandleSelectAll).toHaveBeenCalledWith(true);
	});

	it("個別のチェックボックスが正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const firstFileCheckbox = screen.getAllByRole("checkbox")[1];
		fireEvent.click(firstFileCheckbox);
		expect(mockHandleSelect).toHaveBeenCalledWith("document3.docx", false);
	});

	it("ローディング状態でチェックボックスが無効化されること", () => {
		renderWithProviders(<FileTable {...defaultProps} loading={true} />);
		const checkboxes = screen.getAllByRole("checkbox");
		for (const checkbox of checkboxes) {
			expect(checkbox).toBeDisabled();
		}
	});

	it("ファイルサイズが正しくフォーマットされること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		expect(screen.getByText("1.50 MB")).toBeInTheDocument();
		expect(screen.getByText("500.00 KB")).toBeInTheDocument();
		expect(screen.getByText("2.20 MB")).toBeInTheDocument();
	});

	it("作成日時が正しくフォーマットされること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-15T10:00:00");
		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-14T15:30:00");
		expect(mockFormatDate).toHaveBeenCalledWith("2024-03-16T09:15:00");
	});

	it("サイズでソートが正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const sizeHeader = screen.getByRole("columnheader", { name: /サイズ/ });
		fireEvent.click(sizeHeader);

		const cells = screen
			.getAllByRole("cell")
			.filter((cell) => cell.textContent?.match(/(KB|MB)$/));

		expect(cells[0]).toHaveTextContent("500.00 KB");
		expect(cells[1]).toHaveTextContent("1.50 MB");
		expect(cells[2]).toHaveTextContent("2.20 MB");
	});

	it("作成日時でソートが正しく動作すること", () => {
		renderWithProviders(<FileTable {...defaultProps} />);
		const dateHeader = screen.getByRole("columnheader", { name: /作成日時/ });
		fireEvent.click(dateHeader);

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

		renderWithProviders(
			<FileTable {...defaultProps} files={filesWithInvalidSize} />,
		);
		expect(screen.getByText("0.00 KB")).toBeInTheDocument();
	});
});
