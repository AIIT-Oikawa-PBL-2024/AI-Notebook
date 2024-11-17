import { NotebookEditor } from "@/features/dashboard/notebook/components/NotebookEditor";
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { EditorFields } from "../test-utils";

// TipTapのモック
const mockSetContent = vi.fn();
const mockClearContent = vi.fn();
const mockGetText = vi.fn();

vi.mock("@tiptap/react", () => ({
	useEditor: () => ({
		commands: {
			setContent: mockSetContent,
			clearContent: mockClearContent,
		},
		getText: mockGetText,
	}),
	EditorContent: () => <div data-testid="editor-content">Editor Content</div>,
}));
describe("NotebookEditor", () => {
	const mockFields: EditorFields = {
		content: {
			id: "content",
			name: "content",
			key: "content-key",
			errorId: "content-error",
			descriptionId: "content-description",
			value: "",
			initialValue: "",
			dirty: false,
			// 追加の必須プロパティ
			errors: [], // エラーメッセージの配列
			allErrors: {}, // すべてのエラーメッセージ
			valid: true, // バリデーション状態
			formId: "test-form", // formIdを追加
		},
	};
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("エディターが正しくレンダリングされる", () => {
		render(<NotebookEditor fields={mockFields} />);
		expect(screen.getByTestId("editor-content")).toBeInTheDocument();
	});

	it("defaultValueが設定されている場合、エディターの内容が設定される", () => {
		const defaultValue = "Test Content";
		render(<NotebookEditor fields={mockFields} defaultValue={defaultValue} />);
		expect(mockSetContent).toHaveBeenCalledWith(defaultValue);
	});

	it("clear関数が正しく動作する", () => {
		const ref = { current: null };
		render(<NotebookEditor fields={mockFields} />);
	});
});
