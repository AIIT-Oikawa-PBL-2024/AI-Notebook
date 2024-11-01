import UploadPage from "@/app/(dashboard)/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/utils/withAuth", () => ({
	withAuth: (component: React.ComponentType) => component,
}));

vi.mock("@/features/dashboard/FileUpload", () => ({
	__esModule: true,
	default: () => <div>FileUpload Component</div>,
}));

describe("UploadPage", () => {
	it("ページが正しくレンダリングされること", () => {
		render(<UploadPage />);

		expect(screen.getByText("ファイルアップロード")).toBeInTheDocument();
		expect(screen.getByText("FileUpload Component")).toBeInTheDocument();
	});
});
