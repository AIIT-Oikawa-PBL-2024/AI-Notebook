import GetOutputPage from "@/app/(dashboard)/ai-output/stream/[id]/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("@/features/dashboard/ai-output/stream/GetAIOutputDisplay", () => ({
	GetAIOutputDisplay: vi.fn(() => <div>Mocked GetAIOutputDisplay</div>),
}));

describe("GetOutputPage", () => {
	const defaultProps: React.ComponentProps<typeof GetOutputPage> = {
		params: { id: "123" },
	};

	it("GetAIOutputDisplayコンポーネントが正しいpropsでレンダリングされること", () => {
		render(<GetOutputPage {...defaultProps} />);
		expect(screen.getByText("Mocked GetAIOutputDisplay")).toBeInTheDocument();
	});
});
