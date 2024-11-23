import ExerciseSelectComponent from "@/features/dashboard/ai-exercise/select-exercises/SelectExercises";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { beforeEach, describe, expect, it, vi } from "vitest";

// モックの型定義
type User = {
	id: string;
	name: string;
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
const mockExercises = [
	{
		id: 1,
		title: "選択問題1",
		exercise_type: "multiple_choice",
		response: JSON.stringify({
			content: [
				{
					input: {
						questions: [{ question_text: "Test Question 1" }],
					},
				},
			],
		}),
		created_at: "2024-01-01T00:00:00.000Z",
		files: [
			{
				id: "1",
				file_name: "test1.pdf",
				file_size: "1MB",
				created_at: "2024-01-01",
				user_id: "1",
			},
		],
		user_id: "1",
	},
	{
		id: 2,
		title: "総合問題1",
		exercise_type: "stream",
		response: JSON.stringify({
			content: [
				{
					input: {
						questions: [{ question_text: "Test Question 2" }],
					},
				},
			],
		}),
		created_at: "2024-01-02T00:00:00.000Z",
		files: [
			{
				id: "2",
				file_name: "test2.pdf",
				file_size: "1MB",
				created_at: "2024-01-02",
				user_id: "1",
			},
		],
		user_id: "1",
	},
];

describe("ExerciseSelectComponent", () => {
	const mockRouter = {
		push: vi.fn(),
	};
	const mockAuthFetch = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();

		// ルーターのモック
		(useRouter as ReturnType<typeof vi.fn>).mockReturnValue(mockRouter);

		// 認証のモック
		(useAuth as ReturnType<typeof vi.fn>).mockReturnValue({
			user: { id: "1", name: "Test User" },
		});

		// フェッチのモック
		mockAuthFetch.mockResolvedValue({
			ok: true,
			json: async () => mockExercises,
		} as Response);
		(useAuthFetch as ReturnType<typeof vi.fn>).mockReturnValue(mockAuthFetch);
	});

	it("正しくコンポーネントがレンダリングされること", async () => {
		render(<ExerciseSelectComponent />);

		// ヘッダーが表示されることを確認
		expect(screen.getByText("AI練習問題リスト")).toBeInTheDocument();

		// 検索フィールドが表示されることを確認
		expect(screen.getByRole("searchbox")).toBeInTheDocument();

		// データが読み込まれるのを待つ
		await waitFor(() => {
			expect(screen.getByText("選択問題1")).toBeInTheDocument();
			expect(screen.getByText("総合問題1")).toBeInTheDocument();
		});
	});

	it("検索機能が正しく動作すること", async () => {
		render(<ExerciseSelectComponent />);

		const searchInput = screen.getByRole("searchbox");

		// データ読み込み待ち
		await waitFor(() => {
			expect(screen.getByText("選択問題1")).toBeInTheDocument();
		});

		// 検索実行
		fireEvent.change(searchInput, { target: { value: "総合" } });

		// 検索結果の確認（デバウンス待ち）
		await waitFor(() => {
			expect(screen.queryByText("選択問題1")).not.toBeInTheDocument();
			expect(screen.getByText("総合問題1")).toBeInTheDocument();
		});
	});

	it("問題選択と画面遷移が正しく動作すること", async () => {
		render(<ExerciseSelectComponent />);

		// データ読み込み待ち
		await waitFor(() => {
			expect(screen.getByText("選択問題1")).toBeInTheDocument();
		});

		// 選択問題のラジオボタンを特定して選択
		const rows = screen.getAllByRole("row");
		const multipleChoiceRow = Array.from(rows).find((row) =>
			row.textContent?.includes("選択問題1"),
		);

		// ラジオボタンを見つけて選択
		if (!multipleChoiceRow) {
			throw new Error("選択問題の行が見つかりません");
		}

		const radioButton = multipleChoiceRow.querySelector(
			'input[type="radio"]',
		) as HTMLInputElement;

		if (!radioButton) {
			throw new Error("ラジオボタンが見つかりません");
		}

		fireEvent.click(radioButton);

		// 遷移ボタンをクリック
		const navigateButton = screen.getByText("選択した問題ページを開く");
		fireEvent.click(navigateButton);

		// 正しいページに遷移することを確認
		expect(mockRouter.push).toHaveBeenCalledWith(
			`/ai-exercise/multiple-choice/${mockExercises[0].id}`,
		);
	});

	it("ソート機能が正しく動作すること", async () => {
		render(<ExerciseSelectComponent />);

		await waitFor(() => {
			expect(screen.getByText("選択問題1")).toBeInTheDocument();
		});

		// 問題の種類でソート
		const typeSort = screen.getByText("問題の種類");
		fireEvent.click(typeSort);

		// ソート後のデータ順序を確認（昇順）
		await waitFor(() => {
			const cells = screen.getAllByRole("cell");
			const titleCells = cells.filter((cell) =>
				cell.textContent?.includes("問題"),
			);
			expect(titleCells[0]).toHaveTextContent("選択問題1");
		});

		// もう一度クリックして降順に
		fireEvent.click(typeSort);

		await waitFor(() => {
			const cells = screen.getAllByRole("cell");
			const titleCells = cells.filter((cell) =>
				cell.textContent?.includes("問題"),
			);
			expect(titleCells[0]).toHaveTextContent("総合問題1");
		});
	});

	it("モーダルが正しく表示されること", async () => {
		render(<ExerciseSelectComponent />);

		await waitFor(() => {
			expect(screen.getByText("選択問題1")).toBeInTheDocument();
		});

		// 内容をクリックしてモーダルを開く
		const buttons = screen.getAllByRole("button");
		const contentButton = buttons.find((button) =>
			button.textContent?.includes("Test Question 1"),
		) as HTMLButtonElement;
		fireEvent.click(contentButton);

		// モーダルの表示を確認
		await waitFor(() => {
			expect(screen.getByText("問題の内容")).toBeInTheDocument();
			const modalContent = screen.getAllByText("Test Question 1");
			expect(modalContent[1]).toBeInTheDocument(); // モーダル内のコンテンツを確認
		});
	});

	it("認証エラーが正しく表示されること", async () => {
		// 未認証状態をモック
		(useAuth as ReturnType<typeof vi.fn>).mockReturnValue({ user: null });

		render(<ExerciseSelectComponent />);

		await waitFor(() => {
			expect(screen.getByText("認証が必要です")).toBeInTheDocument();
		});
	});

	it("APIエラーが正しく表示されること", async () => {
		// APIエラーをモック
		mockAuthFetch.mockRejectedValue(new Error("練習問題の取得に失敗しました"));

		render(<ExerciseSelectComponent />);

		await waitFor(() => {
			expect(
				screen.getByText("練習問題の取得に失敗しました"),
			).toBeInTheDocument();
		});
	});
});
