"use client";
import { NotebookForm } from "@/features/dashboard/notebook/components/NotebookForm";
import { useNotebookActions } from "@/features/dashboard/notebook/hooks/useNotebookActions";
import type { Note } from "@/features/dashboard/notebook/types/data";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

type Props = {
	params: { id: string };
};

const EditNotebookPage = ({ params }: Props) => {
	const router = useRouter();
	const { getNotebooks, deleteNotebook } = useNotebookActions();
	const [note, setNote] = useState<Note | undefined>(undefined);
	const [isLoading, setIsLoading] = useState(true);
	const noteId = Number.parseInt(params.id);

	useEffect(() => {
		const fetchNote = async () => {
			if (!noteId) return;

			try {
				const fetchedNotes = await getNotebooks();
				const currentNote = fetchedNotes.find((note) => note.id === noteId);

				if (!currentNote) {
					router.push("/");
					return;
				}
				setNote(currentNote);
			} catch (error) {
				console.error("Note fetch error: ", error);
				router.push("/");
			} finally {
				setIsLoading(false);
			}
		};

		fetchNote();

		return () => {
			setNote(undefined);
			setIsLoading(true);
		};
	}, [noteId, router, getNotebooks]);

	const handleDelete = async () => {
		if (!noteId) return;

		try {
			await deleteNotebook(noteId);
			router.push("/");
		} catch (error) {
			console.error(error);
		}
	};

	if (isLoading) {
		return <div>Loading...</div>;
	}

	return (
		<NotebookForm
			noteId={noteId}
			initialNoteData={note}
			onDelete={handleDelete}
		/>
	);
};

export default EditNotebookPage;
