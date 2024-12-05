import FilePreviewComponent from "@/features/dashboard/select-files/FilePreviewComponent";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// @material-tailwind/react のモック
vi.mock("@material-tailwind/react", () => ({
	Dialog: ({ children, open }: { children: React.ReactNode; open: boolean }) =>
		open ? <div data-testid="dialog">{children}</div> : null,
	DialogHeader: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="dialog-header">{children}</div>
	),
	DialogBody: ({ children }: { children: React.ReactNode }) => (
		<div data-testid="dialog-body">{children}</div>
	),
	IconButton: ({
		children,
		onClick,
	}: { children: React.ReactNode; onClick: () => void }) => (
		<button type="button" data-testid="close-button" onClick={onClick}>
			{children}
		</button>
	),
}));

// グローバルfetchのモック
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe("FilePreviewComponent", () => {
	const defaultProps = {
		fileName: "test.pdf",
		url: "http://example.com/test.pdf",
		contentType: "application/pdf",
		onClose: vi.fn(),
		open: true,
	};

	beforeEach(() => {
		vi.clearAllMocks();
		mockFetch.mockResolvedValue({
			ok: true,
			status: 200,
			headers: new Headers({ "content-type": "application/pdf" }),
		});
	});

	it("PDFプレビューが正しくレンダリングされること", () => {
		render(<FilePreviewComponent {...defaultProps} />);

		const iframe = screen.getByTitle("test.pdf");
		expect(iframe).toBeInTheDocument();
		expect(iframe).toHaveAttribute("src", defaultProps.url);
	});

	it("画像プレビューが正しくレンダリングされること", () => {
		const imageProps = {
			...defaultProps,
			fileName: "test.jpg",
			url: "http://example.com/test.jpg",
			contentType: "image/jpeg",
		};

		render(<FilePreviewComponent {...imageProps} />);

		const img = screen.getByAltText("test.jpg");
		expect(img).toBeInTheDocument();
		expect(img).toHaveAttribute("src", imageProps.url);
	});

	it("動画プレビューが正しくレンダリングされること", () => {
		const videoProps = {
			...defaultProps,
			fileName: "test.mp4",
			url: "http://example.com/test.mp4",
			contentType: "video/mp4",
		};

		const { container } = render(<FilePreviewComponent {...videoProps} />);

		const video = container.querySelector("video");
		expect(video).toBeInTheDocument();

		const source = video?.querySelector("source");
		expect(source).toHaveAttribute("src", videoProps.url);
		expect(source).toHaveAttribute("type", videoProps.contentType);
	});

	it("音声プレビューが正しくレンダリングされること", () => {
		const audioProps = {
			...defaultProps,
			fileName: "test.mp3",
			url: "http://example.com/test.mp3",
			contentType: "audio/mpeg",
		};

		const { container } = render(<FilePreviewComponent {...audioProps} />);

		const audio = container.querySelector("audio");
		expect(audio).toBeInTheDocument();

		const source = audio?.querySelector("source");
		expect(source).toHaveAttribute("src", audioProps.url);
		expect(source).toHaveAttribute("type", audioProps.contentType);
	});

	it("サポートされていないファイル形式の場合、適切なメッセージが表示されること", () => {
		const unsupportedProps = {
			...defaultProps,
			fileName: "test.xyz",
			url: "http://example.com/test.xyz",
			contentType: "application/unknown",
		};

		render(<FilePreviewComponent {...unsupportedProps} />);

		expect(
			screen.getByText("このファイル形式は表示できません"),
		).toBeInTheDocument();
	});

	it("URLがない場合、適切なメッセージが表示されること", () => {
		const noUrlProps = {
			...defaultProps,
			url: "",
		};

		render(<FilePreviewComponent {...noUrlProps} />);

		expect(screen.getByText("URLが見つかりません")).toBeInTheDocument();
	});

	it("閉じるボタンがクリックされたとき、onClose関数が呼ばれること", () => {
		render(<FilePreviewComponent {...defaultProps} />);

		const closeButton = screen.getByTestId("close-button");
		fireEvent.click(closeButton);

		expect(defaultProps.onClose).toHaveBeenCalledTimes(1);
	});

	it("メディアのロードエラー時に適切なエラーメッセージが表示されること", async () => {
		const videoProps = {
			...defaultProps,
			contentType: "video/mp4",
		};

		const { container } = render(<FilePreviewComponent {...videoProps} />);

		const video = container.querySelector("video");
		expect(video).toBeInTheDocument();

		if (video) {
			fireEvent.error(video);
		}

		await waitFor(() => {
			expect(
				screen.getByText("メディアの読み込みに失敗しました"),
			).toBeInTheDocument();
		});
	});
});
