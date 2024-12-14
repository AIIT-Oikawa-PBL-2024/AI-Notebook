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
		// エディタの設定(ショートカットキーを無効化)
		const editor = useEditor({
			extensions: [
				StarterKit.configure({
					heading: false, // 見出し
					bulletList: false, // 箇条書き
					orderedList: false, // 番号付きリスト
					listItem: false, // リストアイテム
					bold: false, // 太字
					italic: false, // 斜体
					strike: false, // 取り消し線
					blockquote: false, // 引用
					code: false, // インラインコード
					codeBlock: false, // コードブロック
					horizontalRule: false, // 水平線
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
				const editorText = editor.getText();
				console.log("Editor onUpdate - テキスト更新:", editorText);
				setInputValue(editorText);
			},
		});

		useEffect(() => {
			if (editor && defaultValue !== undefined) {
				console.log("初期値設定:", defaultValue);
				editor.commands.setContent(defaultValue);
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
