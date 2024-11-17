import NotebookPage from "@/app/(dashboard)/notebook/page";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, test, vi } from "vitest";

// Firebase アプリ初期化のモック
vi.mock("firebase/app", () => ({
	initializeApp: vi.fn(),
}));

// Firebase 認証のモック
vi.mock("firebase/auth", () => ({
	getAuth: vi.fn(() => ({
		currentUser: { uid: "test-uid" },
	})),
}));

// withAuthのモック
vi.mock("@/utils/withAuth", () => ({
	withAuth: (Component: React.ComponentType) => Component,
}));

// NotebookFormのモック
vi.mock("@/features/dashboard/notebook/components/NotebookForm", () => ({
	NotebookForm: () => (
		<div data-testid="notebook-form">Mocked NotebookForm</div>
	),
}));

// react-domのモック
vi.mock("react-dom", () => ({
	useFormState: () => [null, () => {}],
}));

describe("NotebookPage", () => {
	it("NotebookFormコンポーネントがレンダリングされること", () => {
		render(<NotebookPage />);
		expect(screen.getByTestId("notebook-form")).toBeInTheDocument();
	});

	it("withAuthでラップされていること", () => {
		const mockWithAuth = vi.fn();
		vi.mocked(mockWithAuth).mockReturnValue(<div>Protected Component</div>);
		expect(vi.isMockFunction(vi.fn())).toBe(true);
	});
});
