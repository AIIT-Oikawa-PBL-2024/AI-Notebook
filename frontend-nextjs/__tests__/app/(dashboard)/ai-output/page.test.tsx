import CreateOutputPage from "@/app/(dashboard)/ai-output/page";
import { OutputDisplay } from "@/features/dashboard/ai-output/OutputDisplay";
import { useOutputGenerator } from "@/features/dashboard/ai-output/hooks/useOutputGenerator";
import { render, screen, waitFor } from "@testing-library/react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// useOutputGeneratorのモック
vi.mock("@/features/dashboard/ai-output/hooks/useOutputGenerator", () => ({
	useOutputGenerator: vi.fn(),
}));

// withAuthのモック
vi.mock("@/utils/withAuth", () => ({
	withAuth: (Component: React.ComponentType) => Component,
}));

// OutputDisplayのモック
vi.mock("@/features/dashboard/ai-output/OutputDisplay", () => ({
	OutputDisplay: vi.fn(() => (
		<div data-testid="output-display">Output Display</div>
	)),
}));

describe("CreateOutputPage", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it("正常系: ローディング中の状態を表示できる", () => {
		// useOutputGeneratorの返り値をモック
		(useOutputGenerator as Mock).mockReturnValue({
			loading: true,
			error: null,
			output: null,
		});

		render(<CreateOutputPage />);

		expect(OutputDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: true,
				error: null,
				output: null,
			}),
			expect.anything(),
		);
	});

	it("正常系: エクササイズデータを表示できる", async () => {
		const mockOutput = {
			id: "1",
			title: "テストエクササイズ",
			description: "テスト説明",
		};

		(useOutputGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			output: mockOutput,
		});

		render(<CreateOutputPage />);

		await waitFor(() => {
			expect(OutputDisplay).toHaveBeenCalledWith(
				expect.objectContaining({
					loading: false,
					error: null,
					output: mockOutput,
				}),
				expect.anything(),
			);
		});
	});

	it("異常系: エラー状態を表示できる", () => {
		const mockError = new Error("テストエラー");

		(useOutputGenerator as Mock).mockReturnValue({
			loading: false,
			error: mockError,
			output: null,
		});

		render(<CreateOutputPage />);

		expect(OutputDisplay).toHaveBeenCalledWith(
			expect.objectContaining({
				loading: false,
				error: mockError,
				output: null,
			}),
			expect.anything(),
		);
	});

	it("正常系: コンテナのスタイルが正しく適用されている", () => {
		(useOutputGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			output: null,
		});

		render(<CreateOutputPage />);

		const container = screen.getByTestId("output-display").parentElement;
		expect(container).toHaveClass("container", "mx-auto", "p-4");
	});

	it("正常系: OutputDisplayコンポーネントが適切にレンダリングされる", () => {
		(useOutputGenerator as Mock).mockReturnValue({
			loading: false,
			error: null,
			output: null,
		});

		render(<CreateOutputPage />);

		expect(screen.getByTestId("output-display")).toBeInTheDocument();
	});
});
