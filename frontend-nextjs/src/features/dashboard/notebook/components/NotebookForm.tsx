import { useNotebookActions } from "@/features/dashboard/notebook/hooks/useNotebookActions";
import { useForm } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod";
import { useMemo, useRef, useState } from "react";
import { useFormState } from "react-dom";
import { notebookSchema } from "../schema";
import type { InitialNoteData } from "../types/data";
import { NotebookEditor } from "./NotebookEditor";
import { NotebookFormHeader } from "./NotebookHeader";

type NotebookFormProps = {
	noteId?: number;
	initialNoteData?: InitialNoteData;
	onDelete?: () => void;
};

export const NotebookForm = ({
	noteId,
	initialNoteData,
	onDelete,
}: NotebookFormProps) => {
	const editorRef = useRef<{ clear: () => void }>(null);
	const { createNotebook, updateNotebook } = useNotebookActions();
	const formAction = async (prevState: unknown, formData: FormData) => {
		if (noteId) {
			return updateNotebook(noteId, prevState, formData);
		}
		const result = createNotebook(prevState, formData);
		editorRef.current?.clear();

		return result;
	};
	const [lastResult, action] = useFormState(formAction, undefined);

	const [form, fields] = useForm({
		lastResult,
		defaultValue: initialNoteData,
		onValidate({ formData }: { formData: FormData }) {
			return parseWithZod(formData, { schema: notebookSchema });
		},
		shouldValidate: "onBlur",
	});

	const memorizedFields = useMemo(() => fields, [fields]);

	return (
		<form id={form.id} onSubmit={form.onSubmit} action={action} noValidate>
			<div className="flex flex-col items-center justify-start gap-4 m-4 h-screen">
				<NotebookFormHeader
					fields={fields}
					noteId={noteId}
					onDelete={onDelete}
					defaultValue={initialNoteData?.title}
				/>
				<NotebookEditor
					fields={fields}
					defaultValue={initialNoteData?.content}
					ref={editorRef}
				/>
			</div>
		</form>
	);
};
