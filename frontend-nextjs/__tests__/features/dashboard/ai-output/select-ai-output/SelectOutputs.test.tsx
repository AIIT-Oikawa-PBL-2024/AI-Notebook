import OutputSelectComponent from "@/features/dashboard/ai-output/select-ai-output/SelectAIOutput";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { act, render, screen, waitFor } from "@testing-library/react";
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
const mockOutputs = "# テスト問題\n## セクション1\nこれは問題文です。";

describe("OutputSelectComponent", () => {
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
			json: async () => mockOutputs,
		} as Response);
		(useAuthFetch as ReturnType<typeof vi.fn>).mockReturnValue(mockAuthFetch);
	});

	it("正しくコンポーネントがレンダリングされること", async () => {
		await act(async () => {
			render(<OutputSelectComponent />);
		});

		await waitFor(() => {
			// ヘッダーが表示されることを確認
			expect(screen.getByText("AIノートリスト")).toBeInTheDocument();
			// 検索フィールドが表示されることを確認
			expect(screen.getByRole("searchbox")).toBeInTheDocument();
		});
	});

	it("認証エラーが正しく表示されること", async () => {
		// 未認証状態をモック
		(useAuth as ReturnType<typeof vi.fn>).mockReturnValue({ user: null });

		await act(async () => {
			render(<OutputSelectComponent />);
		});

		await waitFor(() => {
			expect(screen.getByText("認証が必要です")).toBeInTheDocument();
		});
	});

	it("APIエラーが正しく表示されること", async () => {
		// APIエラーをモック
		mockAuthFetch.mockRejectedValue(new Error("AI出力の取得に失敗しました"));

		await act(async () => {
			render(<OutputSelectComponent />);
		});

		await waitFor(() => {
			expect(
				screen.getByText("AI出力の取得に失敗しました"),
			).toBeInTheDocument();
		});
	});
});
