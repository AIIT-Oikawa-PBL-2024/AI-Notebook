import type { useForm } from "@conform-to/react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { forwardRef, useEffect, useImperativeHandle } from "react";

type Props = {
	fields: ReturnType<typeof useForm>[1];
	defaultValue?: string;
	onReset?: () => void; // リセット用の関数を追加
};

export const NotebookEditor = forwardRef<{ clear: () => void }, Props>(
	({ fields, defaultValue }, ref) => {
		const editor = useEditor({
			extensions: [StarterKit],
			autofocus: false,
			editable: true,
			content: defaultValue,
			immediatelyRender: false,
			editorProps: {
				attributes: {
					class: "w-full h-96 rounded shadow-sm border border-gray-300",
				},
			},
			onUpdate: ({ editor }) => {
				const contentInput = document.querySelector(
					`input[name="${fields.content.name}"]`,
				) as HTMLInputElement;
				if (contentInput) {
					contentInput.value = editor.getText();
				}
			},
		});

		useEffect(() => {
			if (editor && defaultValue) {
				editor.commands.setContent(defaultValue);
			}
		}, [editor, defaultValue]);

		useImperativeHandle(ref, () => ({
			clear: () => {
				editor?.commands.clearContent(true);
			},
		}));

		return (
			<div className="w-full max-w-4xl h-96">
				<input
					type="hidden"
					key={fields.content.key}
					name={fields.content.name}
				/>
				<EditorContent editor={editor} />
			</div>
		);
	},
);
