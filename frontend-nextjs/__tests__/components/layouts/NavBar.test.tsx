import NavBar from "@/components/layouts/NavBar";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

describe("NavBar", () => {
	it("renders the NavBar component", () => {
		render(<NavBar />);
		expect(screen.getByText("AIノートブック")).toBeInTheDocument();
	});

	it("renders the Home menu item", () => {
		render(<NavBar />);
		expect(screen.getByText("ホーム")).toBeInTheDocument();
	});

	it("renders the File Selection menu item", () => {
		render(<NavBar />);
		expect(screen.getByText("ファイル選択")).toBeInTheDocument();
	});

	it("renders the AI Output menu item", () => {
		render(<NavBar />);
		expect(screen.getByText("AI出力")).toBeInTheDocument();
	});

	it("renders the AI Practice Problems menu item", () => {
		render(<NavBar />);
		expect(screen.getByText("AI練習問題")).toBeInTheDocument();
	});

	it("renders the Notes menu item", () => {
		render(<NavBar />);
		expect(screen.getByText("ノート")).toBeInTheDocument();
	});
});
