import React from "react";
import { render, screen } from "@testing-library/react";
import { expect, describe, it, vi } from "vitest";
import "@testing-library/jest-dom";
import UploadPage from "@/app/page";

// FileUploadコンポーネントのモック
vi.mock("@/features/file/FileUpload", () => ({
  default: () => <div data-testid="file-upload">File Upload Component</div>,
}));

// next/imageのモック
vi.mock("next/image", () => ({
  default: (props: any) => <img {...props} />,
}));

describe("UploadPage", () => {
  it("renders the heading correctly", () => {
    render(<UploadPage />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "ファイルアップロード",
    );
  });

  it("includes the FileUpload component", () => {
    render(<UploadPage />);
    expect(screen.getByTestId("file-upload")).toBeInTheDocument();
  });

  it("displays the image with correct properties", () => {
    render(<UploadPage />);
    const image = screen.getByAltText("アプリの説明画像");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "/pbl-flyer.jpg");
    expect(image).toHaveAttribute("width", "500");
    expect(image).toHaveAttribute("height", "300");
  });
});
