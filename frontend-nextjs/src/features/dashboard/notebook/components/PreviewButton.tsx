import { EyeIcon } from "@heroicons/react/24/solid";

type Props = {
	onClick?: () => void;
};

export const PreviewButton = ({ onClick }: Props) => {
	return (
		<button
			type="button"
			onClick={onClick}
			className="flex items-center justify-center gap-1 px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded hover:bg-gray-50"
		>
			<EyeIcon className="w-5 h-5" />
			<span>プレビュー</span>
		</button>
	);
};
