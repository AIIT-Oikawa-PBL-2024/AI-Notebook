import SelectFilesPage from "@/app/(dashboard)/select-files/page";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

// Mock the dependencies
vi.mock("@/features/dashboard/select-files/FileSelectComponent", () => ({
	default: vi.fn(() => <div>Mocked FileSelectComponent</div>),
}));

vi.mock("@/utils/withAuth", () => ({
	withAuth: vi.fn((Component) => {
		const WithAuthMock = (props: React.ComponentProps<typeof Component>) => {
			return <Component {...props} />;
		};
		return WithAuthMock;
	}),
}));

describe("SelectFilesPage", () => {
	it("should render FileSelectComponent", () => {
		render(<SelectFilesPage />);

		expect(screen.getByText("Mocked FileSelectComponent")).toBeInTheDocument();
	});

	it("should be wrapped with withAuth HOC", () => {
		render(<SelectFilesPage />);

		expect(withAuth).toHaveBeenCalled();
	});

	it("should render correctly with withAuth HOC", () => {
		render(<SelectFilesPage />);

		const component = screen.getByText("Mocked FileSelectComponent");
		expect(component).toBeInTheDocument();
	});
});
