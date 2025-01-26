import SelectNotesComponent from "@/features/dashboard/select-notes/SelectNotes";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import {
	fireEvent,
	render,
	screen,
	waitFor,
	within,
} from "@testing-library/react";
import { act } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { beforeEach, describe, expect, it, vi } from "vitest";

// 型定義
type User = {
	uid: string;
	email: string;
};

type AuthHook = {
	user: User | null;
};

type RouterHook = {
	push: (url: string) => void;
};

type AuthFetchHook = (url: string) => Promise<Response>;

// モックの設定
vi.mock("next/navigation", () => ({
	useRouter: vi.fn(() => ({}) as RouterHook),
}));

vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(() => ({}) as AuthHook),
}));

vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(() => ({}) as unknown as AuthFetchHook),
}));

// テストデータ
const mockNotes = [
	{
		id: 1,
		title: "テストノート1",
		content: "テスト内容1",
		user_id: "test-user",
		updated_at: "2024-03-01T00:00:00Z",
	},
	{
		id: 2,
		title: "テストノート2",
		content: "テスト内容2",
		user_id: "test-user",
		updated_at: "2024-03-02T00:00:00Z",
	},
];

describe("SelectNotesComponent", () => {
	const mockRouter = {
		push: vi.fn(),
	};
	const mockAuthFetch = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();

		// モックの設定
		(useRouter as ReturnType<typeof vi.fn>).mockReturnValue(mockRouter);
		(useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
			user: { uid: "test-user", email: "test@example.com" },
		});
		mockAuthFetch.mockResolvedValue({
			ok: true,
			json: async () => mockNotes,
		} as Response);
		(useAuthFetch as ReturnType<typeof vi.fn>).mockReturnValue(mockAuthFetch);
	});

	it("正しくコンポーネントがレンダリングされること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("ノートリスト")).toBeInTheDocument();
			expect(screen.getByRole("searchbox")).toBeInTheDocument();
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
			expect(screen.getByText("テストノート2")).toBeInTheDocument();
		});
	});

	it("検索機能が正しく動作すること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		const searchInput = screen.getByRole("searchbox");

		await waitFor(() => {
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
		});

		await act(async () => {
			fireEvent.change(searchInput, { target: { value: "テストノート2" } });
		});

		await waitFor(() => {
			expect(screen.queryByText("テストノート1")).not.toBeInTheDocument();
			expect(screen.getByText("テストノート2")).toBeInTheDocument();
		});
	});

	it("ノート選択と画面遷移が正しく動作すること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
		});

		const rows = screen.getAllByRole("row");
		const noteRow = rows.find((row) =>
			row.textContent?.includes("テストノート1"),
		);
		expect(noteRow).toBeInTheDocument();

		let radioButton: HTMLElement | null = null;
		if (noteRow) {
			radioButton = within(noteRow).getByRole("radio");
			expect(radioButton).toBeInTheDocument();
		} else {
			throw new Error("Note row not found");
		}

		await act(async () => {
			if (radioButton) {
				fireEvent.click(radioButton);
			} else {
				throw new Error("Radio button not found");
			}
		});

		const navigateButton = screen.getByText("選択したノートを開く");
		await act(async () => {
			fireEvent.click(navigateButton);
		});

		expect(mockRouter.push).toHaveBeenCalledWith(
			`/notebook/${mockNotes[0].id}`,
		);
	});

	it("ソート機能が正しく動作すること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
		});

		const titleSort = screen.getByText("タイトル");

		await act(async () => {
			fireEvent.click(titleSort);
		});

		await waitFor(() => {
			const cells = screen.getAllByRole("cell");
			const titleCells = cells.filter((cell) =>
				cell.textContent?.includes("テストノート"),
			);
			expect(titleCells[0]).toHaveTextContent("テストノート1");
		});

		await act(async () => {
			fireEvent.click(titleSort);
		});

		await waitFor(() => {
			const cells = screen.getAllByRole("cell");
			const titleCells = cells.filter((cell) =>
				cell.textContent?.includes("テストノート"),
			);
			expect(titleCells[0]).toHaveTextContent("テストノート2");
		});
	});

	it("モーダルが正しく表示されること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
		});

		// モーダルを開くために内容のセル内のボタンを取得
		const contentButton = screen.getByRole("button", { name: /テスト内容1/i });
		expect(contentButton).toBeInTheDocument();

		await act(async () => {
			fireEvent.click(contentButton);
		});

		// モーダルの表示を確認
		await waitFor(() => {
			const dialog = screen.getByRole("dialog");
			expect(dialog).toBeInTheDocument();

			// モーダル内でテキストを確認
			expect(within(dialog).getByText("ノートの内容")).toBeInTheDocument();
			expect(within(dialog).getByText("テスト内容1")).toBeInTheDocument();
		});
	});

	it("認証エラーが正しく表示されること", async () => {
		(useAuth as ReturnType<typeof vi.fn>).mockReturnValue({ user: null });

		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("認証が必要です")).toBeInTheDocument();
		});
	});

	it("APIエラーが正しく表示されること", async () => {
		mockAuthFetch.mockRejectedValue(new Error("ノートの取得に失敗しました"));

		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(
				screen.getByText("ノートの取得に失敗しました"),
			).toBeInTheDocument();
		});
	});

	it("削除機能が正しく動作すること", async () => {
		await act(async () => {
			render(<SelectNotesComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("テストノート1")).toBeInTheDocument();
		});

		const rows = screen.getAllByRole("row");
		const noteRow = rows.find((row) =>
			row.textContent?.includes("テストノート1"),
		);
		expect(noteRow).toBeInTheDocument();

		if (!noteRow) {
			throw new Error("Note row not found");
		}
		const radioButton = within(noteRow).getByRole("radio");
		expect(radioButton).toBeInTheDocument();

		await act(async () => {
			fireEvent.click(radioButton);
		});

		const deleteButton = screen.getByText("選択したノートを削除");
		await act(async () => {
			fireEvent.click(deleteButton);
		});

		await waitFor(() => {
			expect(
				screen.getByText("選択したノートを削除しますか？"),
			).toBeInTheDocument();
		});

		// "実行" ボタンを探して クリック
		const executeButton = screen.getByRole("button", { name: "実行" });
		await act(async () => {
			fireEvent.click(executeButton);
		});

		await waitFor(() => {
			expect(mockAuthFetch).toHaveBeenCalled();
		});
	});
});
