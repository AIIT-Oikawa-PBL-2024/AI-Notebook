import { useNotebookActions } from "@/features/dashboard/notebook/hooks/useNotebookActions";
import { Button } from "@material-tailwind/react";

type DeleteButtonProps = {
	noteId: number;
	onDelete: () => void;
};

export const DeleteButton = ({ noteId, onDelete }: DeleteButtonProps) => {
	const { deleteNotebook } = useNotebookActions();

	const handleDelete = async () => {
		try {
			await deleteNotebook(noteId);
			onDelete();
		} catch (error) {
			console.error("削除エラー:", error);
		}
	};

	return (
		<Button
			type="button"
			variant="outlined"
			className="w-4/9 h-10 p-2 px-4 border border-gray-300"
			onClick={handleDelete}
		>
			削除
		</Button>
	);
};
