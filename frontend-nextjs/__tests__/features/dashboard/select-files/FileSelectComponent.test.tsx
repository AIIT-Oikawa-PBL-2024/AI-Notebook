import FileSelectComponent from "@/features/dashboard/select-files/FileSelectComponent";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { useRouter } from "next/navigation";

// モジュールのモック
vi.mock("@/providers/AuthProvider");
vi.mock("next/navigation");
vi.mock("@/hooks/useAuthFetch");

// 独自のUser型を定義
type User = {
	uid: string;
	// 必要に応じて他のプロパティを追加
};

describe("FileSelectComponent", () => {
	let useAuthMock: Mock;
	let useRouterMock: Mock;
	let useAuthFetchMock: Mock;
	let mockRouter: { push: Mock };

	beforeEach(() => {
		vi.clearAllMocks();
		localStorage.clear();

		// モックの設定
		useAuthMock = useAuth as unknown as Mock;
		useAuthMock.mockReturnValue({
			user: { uid: "test-uid" } as User,
			error: null,
			clearError: vi.fn(),
			reAuthenticate: vi.fn(),
		});

		mockRouter = {
			push: vi.fn(),
		};
		useRouterMock = useRouter as unknown as Mock;
		useRouterMock.mockReturnValue(mockRouter);

		useAuthFetchMock = useAuthFetch as unknown as Mock;
		useAuthFetchMock.mockReturnValue(async (url: string) => {
			if (url.endsWith("/files/")) {
				return {
					ok: true,
					json: async () => [
						{
							file_name: "test1.pdf",
							file_size: "1.5 MB",
							created_at: "2024-03-15T10:00:00",
						},
						{
							file_name: "test2.pdf",
							file_size: "2.0 MB",
							created_at: "2024-03-16T10:00:00",
						},
					],
				};
			}
			if (url.endsWith("/files/delete_files")) {
				return {
					ok: true,
					json: async () => ({ success: true }),
				};
			}
			throw new Error("Unexpected URL");
		});
	});

	it("正常にファイル一覧を表示できること", async () => {
		render(<FileSelectComponent />);

		// ローディング状態の確認
		expect(screen.getByText("ファイル更新")).toBeInTheDocument();

		// ファイル一覧の表示を待機
		await waitFor(() => {
			expect(screen.getByText("test1.pdf")).toBeInTheDocument();
			expect(screen.getByText("test2.pdf")).toBeInTheDocument();
		});
	});

	it("ファイルを選択してAI要約を作成できること", async () => {
		render(<FileSelectComponent />);

		// ファイル一覧の表示を待機
		await waitFor(() => {
			expect(screen.getByText("test1.pdf")).toBeInTheDocument();
		});

		// ファイルを選択
		const checkboxes = screen.getAllByRole("checkbox");
		fireEvent.click(checkboxes[1]); // 最初のファイルを選択

		// タイトルを入力
		const titleInput = screen.getByPlaceholderText(
			"AI要約/練習問題のタイトルを入力してください（最大100文字）",
		);
		fireEvent.change(titleInput, { target: { value: "テストノート" } });

		// AI要約作成ボタンをクリック
		const createButton = screen.getByText("要約");
		fireEvent.click(createButton);

		// ローカルストレージの確認
		expect(localStorage.getItem("selectedFiles")).toBe('["test1.pdf"]');
		expect(localStorage.getItem("title")).toBe("テストノート");
		expect(localStorage.getItem("difficulty")).toBe("medium");

		// ルーティングの確認
		await waitFor(() => {
			expect(mockRouter.push).toHaveBeenCalledWith("/ai-output/stream");
		});
	});

	it("ファイルを選択して練習問題を作成できること", async () => {
		render(<FileSelectComponent />);

		await waitFor(() => {
			expect(screen.getByText("test1.pdf")).toBeInTheDocument();
		});

		const checkboxes = screen.getAllByRole("checkbox");
		fireEvent.click(checkboxes[1]);

		const titleInput = screen.getByPlaceholderText(
			"AI要約/練習問題のタイトルを入力してください（最大100文字）",
		);
		fireEvent.change(titleInput, { target: { value: "テスト演習" } });

		const createButton = screen.getByText("総合問題");
		fireEvent.click(createButton);

		expect(localStorage.getItem("selectedFiles")).toBe('["test1.pdf"]');
		expect(localStorage.getItem("title")).toBe("テスト演習");
		expect(localStorage.getItem("difficulty")).toBe("medium");

		await waitFor(() => {
			expect(mockRouter.push).toHaveBeenCalledWith("/ai-exercise/stream");
		});
	});

	it("ファイルを選択して選択問題を作成できること", async () => {
		render(<FileSelectComponent />);

		await waitFor(() => {
			expect(screen.getByText("test1.pdf")).toBeInTheDocument();
		});

		const checkboxes = screen.getAllByRole("checkbox");
		fireEvent.click(checkboxes[1]);

		const titleInput = screen.getByPlaceholderText(
			"AI要約/練習問題のタイトルを入力してください（最大100文字）",
		);
		fireEvent.change(titleInput, { target: { value: "テスト選択問題" } });

		const createButton = screen.getByText("選択問題テスト");
		fireEvent.click(createButton);

		expect(localStorage.getItem("selectedFiles")).toBe('["test1.pdf"]');
		expect(localStorage.getItem("title")).toBe("テスト選択問題");
		expect(localStorage.getItem("difficulty")).toBe("medium");

		await waitFor(() => {
			expect(mockRouter.push).toHaveBeenCalledWith(
				"/ai-exercise/multiple-choice",
			);
		});
	});

	it("認証エラー時に適切なエラーメッセージが表示されること", async () => {
		// このテスト用にモックを上書き
		useAuthMock.mockReturnValue({
			user: null,
			error: "認証が必要です",
			clearError: vi.fn(),
			reAuthenticate: vi.fn(),
		});

		render(<FileSelectComponent />);

		expect(
			screen.getByText("このページにアクセスするにはログインが必要です"),
		).toBeInTheDocument();
	});
});
