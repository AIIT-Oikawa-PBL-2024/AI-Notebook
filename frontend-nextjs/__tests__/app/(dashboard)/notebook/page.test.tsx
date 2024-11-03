import NotebookListPage from "@/app/(dashboard)/notebook/page";
import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

vi.mock("@/utils/withAuth", () => ({
	withAuth: (component: React.ComponentType) => component,
}));

test("NotebookListPage", () => {
	render(<NotebookListPage />);
	expect(screen.getByText("NotebookListPage")).not.toBeNull();
});
