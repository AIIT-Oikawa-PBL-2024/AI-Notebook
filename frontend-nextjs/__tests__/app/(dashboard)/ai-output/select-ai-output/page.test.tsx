import SelectOutputsPage from "@/app/(dashboard)/ai-output/select-ai-output/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// 依存関係をモック化
vi.mock(
	"@/features/dashboard/ai-output/select-ai-output/SelectAIOutput",
	() => ({
		default: vi.fn(() => <div>Mocked OutputSelectComponent</div>),
	}),
);

describe("SelectOutputsPage", () => {
	it("OutputSelectComponentが正しくレンダリングされること", () => {
		render(<SelectOutputsPage />);

		expect(
			screen.getByText("Mocked OutputSelectComponent"),
		).toBeInTheDocument();
	});
});
