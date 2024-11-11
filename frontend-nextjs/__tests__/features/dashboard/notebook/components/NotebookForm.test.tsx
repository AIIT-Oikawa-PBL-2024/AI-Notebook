import { NotebookForm } from "@/features/dashboard/notebook/components/NotebookForm";
import { useNotebookActions } from "@/features/dashboard/notebook/hooks/useNotebookActions";
import { useForm } from "@conform-to/react";
import {
	act,
	fireEvent,
	render,
	screen,
	waitFor,
} from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";
import type {
	FormFields,
	MaterialButtonProps,
	NotebookActionsType,
	TipTapEditorProps,
} from "../test-utils";

// Firebase アプリ初期化のモック
vi.mock("firebase/app", () => ({
	initializeApp: vi.fn(),
}));

// Firebase 認証のモック
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(() => ({
		currentUser: { uid: "test-uid" },
	})),
}));

// react-dom のモック
vi.mock("react-dom", () => ({
	useFormState: () => [null, () => {}],
}));

// NotebookActionsのモック
vi.mock("@/features/dashboard/notebook/hooks/useNotebookActions", () => ({
	useNotebookActions: vi.fn(),
}));

// AuthFetchのモック
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => vi.fn(),
}));

// TipTapのモック
vi.mock("@tiptap/react", () => ({
	useEditor: () => ({
		commands: {
			setContent: vi.fn(),
			clearContent: vi.fn(),
		},
	}),
	EditorContent: ({ editor }: TipTapEditorProps) => <div>Editor Content</div>,
}));

// @material-tailwind/reactのモック
vi.mock("@material-tailwind/react", () => ({
	Button: ({ children, ...props }: MaterialButtonProps) => (
		<button {...props}>{children}</button>
	),
}));

// @conform-to/reactのモックをファイルのトップレベルで定義
vi.mock("@conform-to/react", () => ({
	useForm: vi.fn(),
}));

describe("NotebookForm", () => {
	const mockCreateNotebook: Mock = vi.fn();
	const mockUpdateNotebook: Mock = vi.fn();
	const mockDeleteNotebook: Mock = vi.fn();
	const mockGetNotebooks: Mock = vi.fn();

	const createMockFields = (values?: {
		title?: string;
		content?: string;
	}): FormFields => ({
		title: {
			id: "title",
			formId: "test-form",
			name: "title",
			value: values?.title ?? "",
			key: "title-key",
			errorId: "title-error",
			descriptionId: "title-description",
			initialValue: values?.title ?? "",
			dirty: false,
			errors: [],
			allErrors: {},
			valid: true,
		},
		content: {
			id: "content",
			formId: "test-form",
			name: "content",
			value: values?.content ?? "",
			key: "content-key",
			errorId: "content-error",
			descriptionId: "content-description",
			initialValue: values?.content ?? "",
			dirty: false,
			errors: [],
			allErrors: {},
			valid: true,
		},
	});

	beforeEach(() => {
		vi.clearAllMocks();
		(useNotebookActions as unknown as Mock).mockReturnValue({
			createNotebook: mockCreateNotebook,
			updateNotebook: mockUpdateNotebook,
			getNotebooks: mockGetNotebooks,
			deleteNotebook: mockDeleteNotebook,
		} satisfies NotebookActionsType);
	});

	it("新規作成時、フォームが正しくレンダリングされる", () => {
		const values = {
			title: "",
			content: "",
		};

		(useForm as Mock).mockReturnValue([
			{ id: "test-form", onSubmit: vi.fn() },
			createMockFields(values),
		]);

		render(<NotebookForm />);
		expect(screen.getByPlaceholderText("ノートタイトル")).toBeInTheDocument();
		expect(screen.getByText("Editor Content")).toBeInTheDocument();
	});

	it("編集時、初期値が正しく設定される", () => {
		const values = {
			title: "Test Title",
			content: "Test Content",
		};

		(useForm as Mock).mockReturnValue([
			{ id: "test-form", onSubmit: vi.fn() },
			createMockFields(values),
		]);

		render(<NotebookForm initialNoteData={values} noteId={1} />);
		expect(screen.getByPlaceholderText("ノートタイトル")).toHaveValue(
			"Test Title",
		);
	});

	it("新規作成時、フォーム送信後にフィールドがクリアされる", async () => {
		let values = {
			title: "New Note",
			content: "New Content",
		};

		(useForm as Mock).mockReturnValue([
			{ id: "test-form", onSubmit: vi.fn() },
			createMockFields(values),
		]);

		mockCreateNotebook.mockResolvedValueOnce({ status: "success" });

		const { rerender } = render(<NotebookForm />);
		const titleInput = screen.getByPlaceholderText("ノートタイトル");
		const submitButton = screen.getByText("保存");

		await act(async () => {
			fireEvent.click(submitButton);
		});

		// フォーム送信後の状態を更新
		values = {
			title: "",
			content: "",
		};

		(useForm as Mock).mockReturnValue([
			{ id: "test-form", onSubmit: vi.fn() },
			createMockFields(values),
		]);

		rerender(<NotebookForm />);

		await waitFor(() => {
			expect(titleInput).toHaveValue("");
		});
	});

	it("更新時、フォーム送信後も値が保持される", async () => {
		const values = {
			title: "Test Title",
			content: "Test Content",
		};

		(useForm as Mock).mockReturnValue([
			{ id: "test-form", onSubmit: vi.fn() },
			createMockFields(values),
		]);

		mockUpdateNotebook.mockResolvedValueOnce({ status: "success" });

		render(<NotebookForm initialNoteData={values} noteId={1} />);
		const titleInput = screen.getByPlaceholderText("ノートタイトル");
		const submitButton = screen.getByText("保存");

		await act(async () => {
			fireEvent.click(submitButton);
		});

		expect(titleInput).toHaveValue("Test Title");
	});
});
