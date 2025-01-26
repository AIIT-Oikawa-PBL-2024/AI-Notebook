import NotesTable from "@/features/dashboard/select-notes/NotesTable";
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

describe("NotesTable コンポーネント", () => {
	// テスト用のノートデータ
	const mockNotes = [
		{
			id: 1,
			title: "First Note",
			content: "This is the first note content.",
			user_id: "user1",
			updated_at: "2023-10-01T10:00:00Z",
		},
		{
			id: 2,
			title: "Second Note",
			content: "This is the second note content.",
			user_id: "user2",
			updated_at: "2023-10-02T12:00:00Z",
		},
	];

	// モック関数の定義
	const mockHandleSelect = vi.fn();
	const mockGetSortIcon = vi.fn().mockReturnValue("🔽");
	const mockHandleSort = vi.fn();
	const mockHandleOpenModal = vi.fn();
	const mockFormatDate = vi
		.fn()
		.mockImplementation((dateStr: string) =>
			new Date(dateStr).toLocaleString(),
		);
	const mockTruncateContent = vi
		.fn()
		.mockImplementation((str: string) => `${str.slice(0, 10)}...`);

	// コンポーネントをレンダリングするヘルパー関数
	const renderComponent = (selectedNoteId: number | null = null) => {
		render(
			<NotesTable
				notes={mockNotes}
				selectedNoteId={selectedNoteId}
				handleSelect={mockHandleSelect}
				handleOpenModal={mockHandleOpenModal}
				getSortIcon={mockGetSortIcon}
				handleSort={mockHandleSort}
				formatDate={mockFormatDate}
				truncateContent={mockTruncateContent}
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
		expect(screen.getByText("内容")).toBeTruthy();
		expect(screen.getByText("更新日時")).toBeTruthy();
	});

	it("すべてのノート行がレンダリングされること", () => {
		renderComponent();

		for (const note of mockNotes) {
			// タイトルの確認
			expect(screen.getByText(note.title)).toBeTruthy();

			// 内容の確認（トランケートされたもの）
			const truncatedContent = `${note.content.slice(0, 10)}...`;
			const truncatedElements = screen.getAllByText(truncatedContent);
			expect(truncatedElements.length).toBeGreaterThan(0);

			// 更新日時の確認
			expect(
				screen.getByText(new Date(note.updated_at).toLocaleString()),
			).toBeTruthy();
		}
	});

	it("ラジオボタンの選択が正しく機能すること", () => {
		renderComponent();

		const radios = screen.getAllByTestId("radio");
		expect(radios.length).toBe(mockNotes.length);

		// 最初のラジオボタンを選択
		fireEvent.click(radios[0]);
		expect(mockHandleSelect).toHaveBeenCalledWith(mockNotes[0].id);

		// 2番目のラジオボタンを選択
		fireEvent.click(radios[1]);
		expect(mockHandleSelect).toHaveBeenCalledWith(mockNotes[1].id);
	});

	it("ヘッダーボタンをクリックするとソートが機能すること", () => {
		renderComponent();

		const sortableHeaders = ["タイトル", "内容", "更新日時"];

		for (const header of sortableHeaders) {
			// 正規表現を使用してボタン名をマッチ
			const button = screen.getByRole("button", {
				name: new RegExp(`^${header} 🔽$`),
			});
			fireEvent.click(button);
			const sortField =
				header === "タイトル"
					? "title"
					: header === "内容"
						? "content"
						: "updated_at";
			expect(mockHandleSort).toHaveBeenCalledWith(sortField);
		}

		expect(mockHandleSort).toHaveBeenCalledTimes(sortableHeaders.length);
	});

	it("ソートアイコンが正しく表示されること", () => {
		renderComponent();

		const sortIcons = screen.getAllByText("🔽");
		expect(sortIcons.length).toBe(3); // 各ソート可能なカラムに1つずつ
	});

	it("内容をクリックするとモーダルが開くこと", () => {
		renderComponent();

		// リテラルの '...' をマッチさせるためにエスケープ
		const contentButtons = screen.getAllByRole("button", { name: /\.\.\.$/ }); // トランケートされた内容のボタン
		expect(contentButtons.length).toBe(mockNotes.length);

		// 最初の内容ボタンをクリック
		fireEvent.click(contentButtons[0]);
		expect(mockHandleOpenModal).toHaveBeenCalledWith(mockNotes[0].content);

		// 2番目の内容ボタンをクリック
		fireEvent.click(contentButtons[1]);
		expect(mockHandleOpenModal).toHaveBeenCalledWith(mockNotes[1].content);
	});

	it("フォーマット関数が正しく適用されること", () => {
		renderComponent();

		for (const note of mockNotes) {
			expect(mockFormatDate).toHaveBeenCalledWith(note.updated_at);
			expect(mockTruncateContent).toHaveBeenCalledWith(note.content);
		}
	});

	it("ノートが選択されていない場合のレンダリングが正しいこと", () => {
		renderComponent(null);

		const radios = screen.getAllByTestId("radio");
		for (const radio of radios) {
			expect((radio as HTMLInputElement).checked).toBe(false);
		}
	});

	it("特定のノートが選択されている場合のレンダリングが正しいこと", () => {
		renderComponent(mockNotes[0].id);

		const radios = screen.getAllByTestId("radio");
		expect((radios[0] as HTMLInputElement).checked).toBe(true);
		expect((radios[1] as HTMLInputElement).checked).toBe(false);
	});
});
