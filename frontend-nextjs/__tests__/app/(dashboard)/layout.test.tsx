import { render, screen } from "@testing-library/react";
import Layout from "@/app/(dashboard)/layout";
import { describe, it, expect, vi } from "vitest";

// Mock NavBar component
vi.mock("@/components/layouts/NavBar", () => ({
	default: () => <nav>Mock NavBar</nav>,
}));

describe("Layout", () => {
	it("renders the NavBar component", () => {
		render(<Layout>Test Content</Layout>);

		// Check if the NavBar component is rendered
		expect(screen.getByText("Mock NavBar")).toBeInTheDocument();
	});

	it("renders children correctly", () => {
		const testContent = "Test Content";
		render(<Layout>{testContent}</Layout>);

		// Check if the children are rendered correctly
		expect(screen.getByText(testContent)).toBeInTheDocument();
	});
});
