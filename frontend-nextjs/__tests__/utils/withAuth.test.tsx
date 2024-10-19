import { useAuth } from "@/providers/AuthProvider";
import { withAuth } from "@/utils/withAuth";
import { render, screen } from "@testing-library/react";
import { useRouter } from "next/navigation";
import React from "react";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

// モックの設定
vi.mock("@/providers/AuthProvider", () => ({
	useAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
	useRouter: vi.fn(),
}));

describe("withAuth HOC", () => {
	const mockPush = vi.fn();
	const MockComponent = () => <div>Protected Content</div>;
	const WrappedComponent = withAuth(MockComponent);

	beforeEach(() => {
		vi.clearAllMocks();
		(useRouter as Mock).mockReturnValue({ push: mockPush });
	});

	it("認証されていないユーザーがアクセスした場合、サインインページにリダイレクトすること", () => {
		(useAuth as Mock).mockReturnValue({ user: null });

		render(<WrappedComponent />);

		expect(mockPush).toHaveBeenCalledWith("/signin");
		expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
	});

	it("認証されたユーザーがアクセスした場合、ラップされたコンポーネントを表示すること", () => {
		(useAuth as Mock).mockReturnValue({
			user: { id: "1", name: "Test User" },
		});

		render(<WrappedComponent />);

		expect(mockPush).not.toHaveBeenCalled();
		expect(screen.getByText("Protected Content")).toBeInTheDocument();
	});

	it("ユーザーの認証状態が変更された場合、適切に対応すること", () => {
		const { rerender } = render(<WrappedComponent />);

		// 最初は未認証
		(useAuth as Mock).mockReturnValue({ user: null });
		rerender(<WrappedComponent />);
		expect(mockPush).toHaveBeenCalledWith("/signin");

		// 認証状態が変更される
		(useAuth as Mock).mockReturnValue({
			user: { id: "1", name: "Test User" },
		});
		rerender(<WrappedComponent />);
		expect(screen.getByText("Protected Content")).toBeInTheDocument();
	});
});
