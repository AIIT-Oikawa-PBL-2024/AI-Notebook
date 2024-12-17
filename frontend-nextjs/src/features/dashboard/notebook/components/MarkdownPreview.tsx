import { XMarkIcon } from "@heroicons/react/24/solid";
import ReactMarkdown from "react-markdown";

type Props = {
	title: string;
	content: string;
	onClose: () => void;
};

export const MarkdownPreview = ({ title, content, onClose }: Props) => {
	return (
		<div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
			<div className="w-full max-w-4xl p-6 mx-4 bg-white rounded-lg max-h-[90vh] overflow-y-auto">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-xl font-bold">{title || "無題のノート"}</h2>
					<button
						type="button"
						onClick={onClose}
						className="p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full"
					>
						<XMarkIcon className="w-6 h-6" />
					</button>
				</div>
				<div className="prose max-w-none markdown-content">
					<ReactMarkdown
						components={{
							h1: ({ node, ...props }) => (
								<h1 className="text-3xl font-bold my-4" {...props} />
							),
							h2: ({ node, ...props }) => (
								<h2 className="text-2xl font-bold my-3" {...props} />
							),
							h3: ({ node, ...props }) => (
								<h3 className="text-xl font-bold my-2" {...props} />
							),
							p: ({ node, ...props }) => <p className="my-2" {...props} />,
							ul: ({ node, ...props }) => (
								<ul className="list-disc pl-4 space-y-0" {...props} />
							),
							ol: ({ node, ...props }) => (
								<ol className="list-decimal pl-4 space-y-0" {...props} />
							),
							li: ({ node, ...props }) => (
								<li className="my-0 leading-normal" {...props} />
							),
							a: ({ node, ...props }) => (
								<a
									className="text-blue-600 hover:text-blue-800 hover:underline"
									{...props}
								/>
							),
							pre: ({ node, ...props }) => (
								<pre
									className="bg-gray-100 p-4 rounded overflow-x-auto my-4"
									{...props}
								/>
							),
							blockquote: ({ node, ...props }) => (
								<blockquote
									className="border-l-4 border-gray-200 pl-4 my-4 italic"
									{...props}
								/>
							),
							hr: ({ node, ...props }) => (
								<hr className="my-8 border-t border-gray-200" {...props} />
							),
						}}
					>
						{content || "本文がありません"}
					</ReactMarkdown>
				</div>
			</div>
		</div>
	);
};
