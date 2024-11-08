import SelectFilesPage from "@/app/(dashboard)/select-files/page";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useRouter } from "next/navigation";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// Providers
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

// Hooks
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: vi.fn(),
}));

// HOC
vi.mock("@/utils/withAuth", () => ({
	withAuth: (Component: React.ComponentType) => Component,
}));

// Navigation
vi.mock("next/navigation", () => ({
	useRouter: () => ({
		push: vi.fn(),
		replace: vi.fn(),
		refresh: vi.fn(),
		back: vi.fn(),
		forward: vi.fn(),
		prefetch: vi.fn(),
	}),
}));

// UI Components
vi.mock("@material-tailwind/react", () => ({
	Alert: vi.fn(({ children }) => <div data-testid="alert">{children}</div>),
	Button: vi.fn(({ children, onClick, disabled }) => (
		<button
			type="button"
			onClick={onClick}
			disabled={disabled}
			data-testid={`button-${children.toString().toLowerCase().replace(/\s+/g, "-")}`}
		>
			{children}
		</button>
	)),
	Card: vi.fn(({ children, className }) => (
		<div className={className}>{children}</div>
	)),
	CardBody: vi.fn(({ children, className }) => (
		<div className={className}>{children}</div>
	)),
	CardHeader: vi.fn(({ children, className }) => (
		<div className={className}>{children}</div>
	)),
	Checkbox: vi.fn(({ onChange, checked, disabled, name }) => (
		<input
			type="checkbox"
			onChange={(e) => onChange(e)}
			checked={checked}
			disabled={disabled}
			data-testid="checkbox-all"
		/>
	)),
	Input: vi.fn(({ value, onChange, placeholder }) => (
		<input
			type="text"
			value={value}
			onChange={onChange}
			placeholder={placeholder}
			data-testid="title-input"
		/>
	)),
	Spinner: vi.fn(() => <div data-testid="spinner">Loading...</div>),
	Typography: vi.fn(({ children, className }) => (
		<div className={className}>{children}</div>
	)),
}));

describe("SelectFilesPage", () => {
	const mockRouter = useRouter();
	const mockAuthFetch = vi.fn();
	const mockClearError = vi.fn();
	const mockReAuthenticate = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();

		// Auth状態のモック
		(useAuth as Mock).mockReturnValue({
			user: { uid: "test-uid" },
			error: null,
			clearError: mockClearError,
			reAuthenticate: mockReAuthenticate,
		});

		// APIフェッチのモック
		(useAuthFetch as Mock).mockReturnValue(mockAuthFetch);

		// ストレージのモック
		const localStorageMock = {
			getItem: vi.fn(),
			setItem: vi.fn(),
			removeItem: vi.fn(),
			clear: vi.fn(),
		};
		Object.defineProperty(window, "localStorage", { value: localStorageMock });
	});

	it("正常系: ファイル一覧を取得・表示できる", async () => {
		// モックデータの準備
		const mockFiles = [
			{
				file_name: "test1.txt",
				file_size: "1KB",
				created_at: "2024-01-01T00:00:00Z",
				select: false,
			},
		];

		// APIレスポンスのモック
		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockFiles),
		});

		render(<SelectFilesPage />);

		await waitFor(() => {
			expect(screen.getByText("test1.txt")).toBeInTheDocument();
			expect(screen.getByText("1KB")).toBeInTheDocument();
		});
	});

	it("異常系: ファイル取得でエラーが発生した場合、エラーメッセージを表示する", async () => {
		// エラーレスポンスのモック
		mockAuthFetch.mockResolvedValueOnce({
			ok: false,
			json: () => Promise.resolve({ message: "ファイルの取得に失敗しました" }),
		});

		render(<SelectFilesPage />);

		await waitFor(() => {
			const alerts = screen.getAllByTestId("alert");
			expect(alerts[0]).toHaveTextContent("ファイルの取得に失敗しました");
		});
	});

	it("異常系: 認証エラーの場合、再認証を試みる", async () => {
		// 認証エラーのモック
		mockAuthFetch.mockRejectedValueOnce({
			message: "token expired",
		});

		render(<SelectFilesPage />);

		await waitFor(() => {
			expect(mockReAuthenticate).toHaveBeenCalled();
		});
	});

	it("正常系: ファイルを選択してAIノートを作成できる", async () => {
		// モックデータの準備
		const mockFiles = [
			{
				file_name: "test1.txt",
				file_size: "1KB",
				created_at: "2024-01-01T00:00:00Z",
				select: false,
			},
		];

		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockFiles),
		});

		render(<SelectFilesPage />);

		await waitFor(async () => {
			// ファイル選択
			const checkboxes = screen.getAllByTestId("checkbox-all");
			fireEvent.click(checkboxes[1]);

			// タイトル入力
			const titleInput = screen.getByTestId("title-input");
			fireEvent.change(titleInput, { target: { value: "テストタイトル" } });

			// AIノート作成
			const createButton = screen.getByText("AIノート作成");
			fireEvent.click(createButton);

			// 検証
			expect(localStorage.setItem).toHaveBeenCalledWith(
				"selectedFiles",
				JSON.stringify(["test1.txt"]),
			);
			expect(localStorage.setItem).toHaveBeenCalledWith(
				"title",
				"テストタイトル",
			);
		});
	});

	it("正常系: リセットボタンが正しく動作する", async () => {
		// モックデータの準備
		const mockFiles = [
			{
				file_name: "test1.txt",
				file_size: "1KB",
				created_at: "2024-01-01T00:00:00Z",
				select: true,
			},
		];

		mockAuthFetch.mockResolvedValueOnce({
			ok: true,
			json: () => Promise.resolve(mockFiles),
		});

		render(<SelectFilesPage />);

		await waitFor(() => {
			// リセット操作
			const resetButton = screen.getByTestId("button-リセット");
			fireEvent.click(resetButton);

			// 検証
			expect(mockClearError).toHaveBeenCalled();
			expect(screen.queryByText("test1.txt")).not.toBeInTheDocument();
		});
	});
});
