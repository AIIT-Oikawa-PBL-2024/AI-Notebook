import { useNoteInitialData } from "@/features/dashboard/ai-output/select-ai-output/useNoteInitialData"; // 追加
import { useNotebookActions } from "@/features/dashboard/notebook/hooks/useNotebookActions";
import { useForm } from "@conform-to/react";
import { parseWithZod } from "@conform-to/zod";
import { useEffect, useMemo, useRef, useState } from "react";
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
	const headerRef = useRef<{ clear: () => void }>(null);
	const { createNotebook, updateNotebook } = useNotebookActions();
	const { getAndRemoveInitialData } = useNoteInitialData();
	const [localStorageData, setLocalStorageData] = useState<
		InitialNoteData | undefined
	>(undefined);

	// LocalStorage からデータを取得
	useEffect(() => {
		const data = getAndRemoveInitialData();
		if (data) {
			setLocalStorageData(data);
		}
	}, [getAndRemoveInitialData]);

	// 有効な初期データを決定
	const effectiveInitialData = useMemo(
		() => localStorageData || initialNoteData,
		[localStorageData, initialNoteData],
	);

	const formAction = async (prevState: unknown, formData: FormData) => {
		if (noteId) {
			return updateNotebook(noteId, prevState, formData);
		}
		const result = createNotebook(prevState, formData);
		editorRef.current?.clear();
		headerRef.current?.clear();

		return result;
	};

	const [lastResult, action] = useFormState(formAction, undefined);

	const [form, fields] = useForm({
		lastResult,
		defaultValue: effectiveInitialData,
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
					defaultValue={effectiveInitialData?.title}
					ref={headerRef}
				/>
				<NotebookEditor
					fields={fields}
					defaultValue={effectiveInitialData?.content}
					ref={editorRef}
				/>
			</div>
		</form>
	);
};
