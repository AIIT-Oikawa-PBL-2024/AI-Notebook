import SelectFilesPage from "@/app/(dashboard)/select-files/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("@/features/dashboard/select-files/FileSelectComponent", () => ({
	default: vi.fn(() => <div>Mocked FileSelectComponent</div>),
}));

describe("SelectFilesPage", () => {
	it("FileSelectComponentが正しくレンダリングされること", () => {
		render(<SelectFilesPage />);

		expect(screen.getByText("Mocked FileSelectComponent")).toBeInTheDocument();
	});
});
