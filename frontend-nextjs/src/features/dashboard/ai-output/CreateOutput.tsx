import { useOutputContent } from "@/features/dashboard/ai-output/hooks/useOutputContent";
import { useEffect, useState } from "react";
import type { FC } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const CreateOutput: FC = () => {
	const fileNames = ["3_規範的なプロセスモデル.pdf"];
	const { contents, loading, error, fetchOutputContent } = useOutputContent();
	const [isProcessing, setIsProcessing] = useState(false);

	useEffect(() => {
		// コンポーネントがマウントされた時のみ実行
		if (!isProcessing) {
			setIsProcessing(true);
			fetchOutputContent(fileNames);
		}
	}, [isProcessing, fetchOutputContent]);

	return (
		<div className="p-4">
			{loading && <p className="text-gray-600">読み込み中...</p>}
			{error && <p className="text-red-500">{error}</p>}
			<ReactMarkdown
				remarkPlugins={[remarkGfm]}
				components={{
					// 改行や段落を適切に表示するためのカスタマイズ
					p: ({ node, ...props }) => <p className="mb-4" {...props} />,
					br: () => <br />,
				}}
			>
				{contents}
			</ReactMarkdown>
		</div>
	);
};

export default CreateOutput;
