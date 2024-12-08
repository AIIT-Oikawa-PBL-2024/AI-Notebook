import type { Metadata } from "next";

export const metadata: Metadata = {
	title: "404 | AI Notebook",
};

export default function NotFound() {
	return (
		<div className="flex w-full h-screen justify-center items-center bg-white flex-col gap-3">
			<h1 className="text-6xl text-red-700">404</h1>
			<h3 className="text-lg text-black">
				お探しのページは見つかりませんでした
			</h3>
		</div>
	);
}
