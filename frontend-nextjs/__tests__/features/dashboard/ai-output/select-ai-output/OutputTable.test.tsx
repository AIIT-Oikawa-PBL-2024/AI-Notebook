import OutputTable from "@/features/dashboard/ai-output/select-ai-output/OutputTable";
import { fireEvent, render, screen } from "@testing-library/react";
import type React from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// @material-tailwind/react コンポーネントのモック
vi.mock("@material-tailwind/react", () => ({
	Radio: ({
		checked,
		onChange,
	}: {
		checked: boolean;
		onChange: () => void;
	}) => (
		<input
			type="radio"
			checked={checked}
			onChange={onChange}
			data-testid="radio"
		/>
	),
	Typography: ({ children }: { children: React.ReactNode }) => (
		<span>{children}</span>
	),
}));

describe("OutputTable コンポーネント", () => {
	// テスト用の出力データ
	const mockOutputs = [
		{
			id: 1,
			title: "First Output",
			output: "This is the first output.",
			user_id: "user1",
			created_at: "2023-10-01T10:00:00Z",
			files: [
				{
					id: "f1",
					file_name: "file1.txt",
					file_size: "2KB",
					created_at: "2023-10-01",
					user_id: "user1",
				},
			],
			style: "Style1",
		},
		{
			id: 2,
			title: "Second Output",
			output: "This is the second output.",
			user_id: "user2",
			created_at: "2023-10-02T12:00:00Z",
			files: [
				{
					id: "f2",
					file_name: "file2.txt",
					file_size: "3KB",
					created_at: "2023-10-02",
					user_id: "user2",
				},
				{
					id: "f3",
					file_name: "file3.txt",
					file_size: "1KB",
					created_at: "2023-10-02",
					user_id: "user2",
				},
			],
			style: "Style2",
		},
	];

	// モック関数の定義
	const mockHandleSelect = vi.fn();
	const mockGetSortIcon = vi.fn().mockReturnValue("🔽");
	const mockHandleSort = vi.fn();
	const mockHandleOpenModal = vi.fn();
	const mockFormatStyle = vi
		.fn()
		.mockImplementation((style: string | null) => `Formatted ${style}`);
	const mockFormatDate = vi
		.fn()
		.mockImplementation((dateStr: string) =>
			new Date(dateStr).toLocaleString(),
		);
	const mockTruncateResponse = vi
		.fn()
		.mockImplementation((str: string) => `${str.slice(0, 10)}...`);

	// コンポーネントをレンダリングするヘルパー関数
	const renderComponent = (selectedOutputId: number | null = null) => {
		render(
			<OutputTable
				outputs={mockOutputs}
				selectedOutputId={selectedOutputId}
				handleSelect={mockHandleSelect}
				getSortIcon={mockGetSortIcon}
				handleSort={mockHandleSort}
				handleOpenModal={mockHandleOpenModal}
				formatStyle={mockFormatStyle}
				formatDate={mockFormatDate}
				truncateResponse={mockTruncateResponse}
			/>,
		);
	};

	// 各テストの前にモック関数をリセット
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("テーブルヘッダーが正しくレンダリングされること", () => {
		renderComponent();

		expect(screen.getByText("選択")).toBeTruthy();
		expect(screen.getByText("タイトル")).toBeTruthy();
		expect(screen.getByText("関連ファイル")).toBeTruthy();
		expect(screen.getByText("スタイル")).toBeTruthy();
		expect(screen.getByText("内容")).toBeTruthy();
		expect(screen.getByText("作成日時")).toBeTruthy();
	});

	it("すべての出力行がレンダリングされること", () => {
		renderComponent();

		for (const output of mockOutputs) {
			// タイトルの確認
			expect(screen.getByText(output.title)).toBeTruthy();

			// 関連ファイルの確認
			const fileNames = output.files.map((f) => f.file_name).join(", ");
			expect(screen.getByText(fileNames)).toBeTruthy();

			// スタイルの確認
			expect(screen.getByText(`Formatted ${output.style}`)).toBeTruthy();

			// 内容の確認（トランケートされたもの）
			// getAllByText を使用して複数の要素を取得
			const truncatedText = `${output.output.slice(0, 10)}...`;
			const truncatedElements = screen.getAllByText(truncatedText);
			expect(truncatedElements.length).toBeGreaterThan(0);

			// 作成日時の確認
			expect(
				screen.getByText(new Date(output.created_at).toLocaleString()),
			).toBeTruthy();
		}
	});

	it("ラジオボタンの選択が正しく機能すること", () => {
		renderComponent();

		const radios = screen.getAllByTestId("radio");
		expect(radios.length).toBe(mockOutputs.length);

		// 最初のラジオボタンを選択
		fireEvent.click(radios[0]);
		expect(mockHandleSelect).toHaveBeenCalledWith(mockOutputs[0].id);

		// 2番目のラジオボタンを選択
		fireEvent.click(radios[1]);
		expect(mockHandleSelect).toHaveBeenCalledWith(mockOutputs[1].id);
	});

	it("ヘッダーボタンをクリックするとソートが機能すること", () => {
		renderComponent();

		const sortableHeaders = [
			"タイトル",
			"関連ファイル",
			"スタイル",
			"内容",
			"作成日時",
		];

		for (const header of sortableHeaders) {
			// 正規表現を使用してボタン名をマッチ
			const button = screen.getByRole("button", {
				name: new RegExp(`^${header} 🔽$`),
			});
			fireEvent.click(button);
			const sortField =
				header === "タイトル"
					? "title"
					: header === "関連ファイル"
						? "files"
						: header === "スタイル"
							? "style"
							: header === "内容"
								? "output"
								: "created_at";
			expect(mockHandleSort).toHaveBeenCalledWith(sortField);
		}

		expect(mockHandleSort).toHaveBeenCalledTimes(sortableHeaders.length);
	});

	it("ソートアイコンが正しく表示されること", () => {
		renderComponent();

		const sortIcons = screen.getAllByText("🔽");
		expect(sortIcons.length).toBe(5); // 各ソート可能なカラムに1つずつ
	});

	it("内容をクリックするとモーダルが開くこと", () => {
		renderComponent();

		// リテラルの '...' をマッチさせるためにエスケープ
		const contentButtons = screen.getAllByRole("button", { name: /\.\.\.$/ }); // トランケートされた内容のボタン
		expect(contentButtons.length).toBe(mockOutputs.length);

		// 最初の内容ボタンをクリック
		fireEvent.click(contentButtons[0]);
		expect(mockHandleOpenModal).toHaveBeenCalledWith(mockOutputs[0].output);

		// 2番目の内容ボタンをクリック
		fireEvent.click(contentButtons[1]);
		expect(mockHandleOpenModal).toHaveBeenCalledWith(mockOutputs[1].output);
	});

	it("フォーマット関数が正しく適用されること", () => {
		renderComponent();

		for (const output of mockOutputs) {
			expect(mockFormatStyle).toHaveBeenCalledWith(output.style);
			expect(mockFormatDate).toHaveBeenCalledWith(output.created_at);
			expect(mockTruncateResponse).toHaveBeenCalledWith(output.output);
		}
	});

	it("出力が選択されていない場合のレンダリングが正しいこと", () => {
		renderComponent(null);

		const radios = screen.getAllByTestId("radio");
		for (const radio of radios) {
			expect((radio as HTMLInputElement).checked).toBe(false);
		}
	});

	it("特定の出力が選択されている場合のレンダリングが正しいこと", () => {
		renderComponent(mockOutputs[0].id);

		const radios = screen.getAllByTestId("radio");
		expect((radios[0] as HTMLInputElement).checked).toBe(true);
		expect((radios[1] as HTMLInputElement).checked).toBe(false);
	});
});
