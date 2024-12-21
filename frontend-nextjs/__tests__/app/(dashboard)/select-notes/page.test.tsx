import SelectNotesPage from "@/app/(dashboard)/select-notes/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// 依存関係をモック化
vi.mock("@/features/dashboard/select-notes/SelectNotes", () => ({
	default: vi.fn(() => <div>Mocked SelectNotesComponent</div>),
}));

describe("SelectNotesPage", () => {
	it("SelectNotesComponentが正しくレンダリングされること", () => {
		render(<SelectNotesPage />);

		expect(screen.getByText("Mocked SelectNotesComponent")).toBeInTheDocument();
	});
});
