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
	const noteId = Number.parseInt(params.id);

	useEffect(() => {
		let isMounted = true;
		const fetchNote = async (noteId: number) => {
			try {
				const fetchedNotes = await getNotebooks();
				const currentNote = fetchedNotes.find((note) => note.id === noteId);
				if (!currentNote) {
					router.push("/");
					return;
				}
				if (isMounted) {
					setNote(currentNote);
				}
			} catch (error) {
				console.error("Note fetch error: ", error);
				router.push("/");
			}
		};
		if (noteId) {
			fetchNote(noteId);
		}
		return () => {
			isMounted = false;
		};
	}, [noteId, getNotebooks, router]);

	const handleDelete = async () => {
		if (!noteId) return;

		try {
			await deleteNotebook(noteId);
		} catch (error) {
			console.error(error);
		}
		router.push("/");
	};

	return (
		<NotebookForm
			noteId={noteId}
			initialNoteData={note}
			onDelete={handleDelete}
		/>
	);
};

export default EditNotebookPage;
