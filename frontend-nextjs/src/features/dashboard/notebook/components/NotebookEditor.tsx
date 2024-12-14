import type { useForm } from "@conform-to/react";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { forwardRef, useEffect, useImperativeHandle, useState } from "react";

type Props = {
	fields: ReturnType<typeof useForm>[1];
	defaultValue?: string;
	onReset?: () => void;
};

export const NotebookEditor = forwardRef<{ clear: () => void }, Props>(
	({ fields, defaultValue }, ref) => {
		const [inputValue, setInputValue] = useState(defaultValue || "");

		const editor = useEditor({
			extensions: [
				StarterKit.configure({
					heading: false,
					bulletList: false,
					orderedList: false,
					listItem: false,
					bold: false,
					italic: false,
					strike: false,
					blockquote: false,
					code: false,
					codeBlock: false,
					horizontalRule: false,
				}),
			],
			autofocus: false,
			editable: true,
			content: defaultValue,
			immediatelyRender: false,
			editorProps: {
				attributes: {
					class:
						"w-full h-full rounded shadow-sm border border-gray-300 overflow-y-auto p-4",
				},
			},
			onUpdate: ({ editor }) => {
				// HTMLコンテンツを取得し、改行を保持する形に変換
				const content = editor.getHTML();
				// <p>タグをnewlineに変換
				const processedContent = content
					.replace(/<p>/g, "")
					.replace(/<\/p>/g, "\n")
					.replace(/<br\/?>/g, "\n")
					.trim();

				console.log("Editor onUpdate - テキスト更新:", processedContent);
				setInputValue(processedContent);
			},
		});

		useEffect(() => {
			if (editor && defaultValue !== undefined) {
				console.log("初期値設定:", defaultValue);
				// 初期値の改行を<p>タグに変換してセット
				const formattedContent = defaultValue
					.split("\n")
					.map((line) => `<p>${line}</p>`)
					.join("");
				editor.commands.setContent(formattedContent);
				setInputValue(defaultValue);
			}
		}, [editor, defaultValue]);

		useImperativeHandle(ref, () => ({
			clear: () => {
				console.log("エディタのクリア実行");
				editor?.commands.clearContent(true);
				setInputValue("");
			},
		}));

		useEffect(() => {
			const form = document
				.querySelector(`input[name="${fields.content.name}"]`)
				?.closest("form");
			if (form) {
				form.addEventListener("submit", (e) => {
					console.log("フォーム送信時の値:", inputValue);
				});
			}
		}, [fields.content.name, inputValue]);

		return (
			<div className="w-full max-w-4xl h-[36rem] overflow-hidden">
				<input
					type="hidden"
					key={fields.content.key}
					name={fields.content.name}
					value={inputValue}
					onChange={(e) => setInputValue(e.target.value)}
				/>
				<div className="h-full overflow-hidden">
					<EditorContent editor={editor} className="h-full" />
				</div>
			</div>
		);
	},
);
