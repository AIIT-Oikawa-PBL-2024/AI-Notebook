import type { useForm } from "@conform-to/react";
import {
	forwardRef,
	useEffect,
	useImperativeHandle,
	useRef,
	useState,
} from "react";
import { DeleteButton } from "./DeleteButton";
import { MarkdownPreview } from "./MarkdownPreview";
import { PreviewButton } from "./PreviewButton";
import { SaveButton } from "./SaveButton";

type Props = {
	fields: ReturnType<typeof useForm>[1];
	noteId?: number;
	onDelete?: () => void;
	defaultValue?: string;
};

export type NotebookFormHeaderRef = {
	clear: () => void;
};

export const NotebookFormHeader = forwardRef<NotebookFormHeaderRef, Props>(
	({ fields, noteId, onDelete, defaultValue }, ref) => {
		const [inputValue, setInputValue] = useState(defaultValue ?? "");
		const [isPreviewOpen, setIsPreviewOpen] = useState(false);
		const titleInputRef = useRef<HTMLInputElement>(null);
		const { title, content } = fields;

		// defaultValue が変更された時に入力値を更新
		useEffect(() => {
			setInputValue(defaultValue ?? "");
		}, [defaultValue]);

		useImperativeHandle(ref, () => ({
			clear: () => {
				console.log("NotebookFormHeader clear called");
				console.log("titleInputRef exists:", !!titleInputRef.current);
				console.log("Previous value:", inputValue);
				setInputValue("");
				if (titleInputRef.current) {
					titleInputRef.current.value = "";
				}
				console.log("After clear value: ", "");
			},
		}));

		const handlePreviewClick = () => {
			if (typeof content?.value !== "string" || !content.value.trim()) {
				alert("本文を入力してください");
				return;
			}
			setIsPreviewOpen(true);
		};

		return (
			<div className="flex w-full max-w-4xl gap-4 items-center">
				<div className="flex gap-4 items-center w-full">
					<input
						ref={titleInputRef}
						type="text"
						key={title.key}
						name={title.name}
						value={inputValue}
						onChange={(e) => setInputValue(e.target.value)}
						className="flex-grow w-4/9 h-10 p-2 border border-gray-300 appearance-none rounded"
						placeholder="ノートタイトル"
					/>
					<PreviewButton onClick={handlePreviewClick} />
					<SaveButton />
					{noteId && onDelete && (
						<DeleteButton noteId={noteId} onDelete={onDelete} />
					)}
				</div>
				{isPreviewOpen && (
					<MarkdownPreview
						title={inputValue}
						content={typeof content?.value === "string" ? content.value : ""}
						onClose={() => setIsPreviewOpen(false)}
					/>
				)}
			</div>
		);
	},
);

NotebookFormHeader.displayName = "NotebookFormHeader";
