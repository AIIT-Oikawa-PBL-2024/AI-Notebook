import { render, screen } from "@testing-library/react";
import DashboardError from "@/app/(dashboard)/error";
import { describe, expect, it, vi } from "vitest";

// Material Tailwindのコンポーネントのモック
vi.mock("@material-tailwind/react", () => ({
  Alert: ({ children, icon, className }: any) => (
    <div data-testid="alert" className={className}>
      {icon}
      {children}
    </div>
  ),
}));

describe("DashboardError", () => {
  it("正常系: エラーメッセージが表示される", () => {
    render(<DashboardError />);
    expect(
      screen.getByText("エラーが発生しました。もう一度お試しください。"),
    ).toBeInTheDocument();
  });

  it("正常系: アイコンが表示される", () => {
    render(<DashboardError />);
    const svg = screen.getByRole("img", { name: "error" });
    expect(svg).toBeInTheDocument();
  });

  it("正常系: 適切なスタイルが適用されている", () => {
    render(<DashboardError />);
    const container = screen.getByTestId("alert").parentElement;
    expect(container).toHaveClass(
      "flex items-start mt-32 justify-center min-h-screen text-center",
    );
  });
});
