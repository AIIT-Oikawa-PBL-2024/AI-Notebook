import { NotebookFormHeader } from "@/features/dashboard/notebook/components/NotebookHeader";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { HeaderFields, MaterialButtonProps } from "../test-utils";

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

// AuthFetchのモック
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () => vi.fn(),
}));

vi.mock("@material-tailwind/react", () => ({
	Button: ({ children, ...props }: MaterialButtonProps) => (
		<button {...props}>{children}</button>
	),
}));

// next/navigation のモック
vi.mock("next/navigation", () => ({
	useRouter: vi.fn(() => ({
		push: vi.fn(),
		replace: vi.fn(),
	})),
}));

describe("NotebookFormHeader", () => {
	const mockFields: HeaderFields = {
		title: {
			name: "title",
			key: "test-key",
			formId: "test-form",
			id: "title-field",
			errorId: "title-error",
			descriptionId: "title-description",
			value: "",
			initialValue: "",
			dirty: false,
			errors: [],
			allErrors: {},
			valid: true,
		},
	};

	it("タイトル入力フィールドが正しくレンダリングされる", () => {
		render(<NotebookFormHeader fields={mockFields} />);
		const titleInput = screen.getByPlaceholderText("ノートタイトル");
		expect(titleInput).toBeInTheDocument();
		expect(titleInput).toHaveAttribute("name", "title");
	});

	it("デフォルト値が正しく設定される", () => {
		const defaultValue = "Test Title";
		render(
			<NotebookFormHeader fields={mockFields} defaultValue={defaultValue} />,
		);
		const titleInput = screen.getByPlaceholderText("ノートタイトル");
		expect(titleInput).toHaveValue(defaultValue);
	});

	it("保存ボタンが常に表示される", () => {
		render(<NotebookFormHeader fields={mockFields} />);
		expect(screen.getByText("保存")).toBeInTheDocument();
	});

	it("削除ボタンは noteId と onDelete が存在する場合のみ表示される", () => {
		const { rerender } = render(<NotebookFormHeader fields={mockFields} />);
		// noteId と onDelete がない場合は削除ボタンは表示されない
		expect(screen.queryByText("削除")).not.toBeInTheDocument();

		// noteId のみの場合も削除ボタンは表示されない
		rerender(<NotebookFormHeader fields={mockFields} noteId={1} />);
		expect(screen.queryByText("削除")).not.toBeInTheDocument();

		// noteId と onDelete の両方がある場合のみ削除ボタンが表示される
		const mockOnDelete = vi.fn();
		rerender(
			<NotebookFormHeader
				fields={mockFields}
				noteId={1}
				onDelete={mockOnDelete}
			/>,
		);
		expect(screen.getByText("削除")).toBeInTheDocument();
	});
});
