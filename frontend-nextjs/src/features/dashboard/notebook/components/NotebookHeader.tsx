import type { useForm } from "@conform-to/react";
import { DeleteButton } from "./DeleteButton";
import { SaveButton } from "./SaveButton";

type Props = {
	fields: ReturnType<typeof useForm>[1];
	noteId?: number; // 既存のnoteの編集
	onDelete?: () => void; //  削除時の処理
	defaultValue?: string;
};

export const NotebookFormHeader = ({
	fields,
	noteId,
	onDelete,
	defaultValue,
}: Props) => {
	const { title } = fields;

	return (
		<div className="flex w-full max-w-4xl gap-4">
			<input
				type="text"
				key={title.key}
				name={title.name}
				defaultValue={defaultValue ?? ""}
				className="flex-grow w-4/9 h-10 p-2 border border-gray-300 appearance-none rounded"
				placeholder="ノートタイトル"
			/>
			<SaveButton />
			{noteId && onDelete && (
				<DeleteButton noteId={noteId} onDelete={onDelete} />
			)}
		</div>
	);
};
