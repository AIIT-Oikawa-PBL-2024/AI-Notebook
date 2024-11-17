import type { useForm } from "@conform-to/react";
import type { FieldMetadata } from "@conform-to/react";
import type { Editor } from "@tiptap/react";
import type { ReactNode } from "react";
import type { Mock } from "vitest";

// 共通のフィールド型
type FormField = {
	key: string;
	name: string;
	value?: string;
	error?: string;
};

// EditorFieldsの型を@conform-to/reactの型に合わせる
export type EditorFields = {
	content: FieldMetadata<string>;
};

// 他の型定義は変更なし
export type HeaderFields = {
	title: FieldMetadata<string>;
};

export type MaterialButtonProps = {
	children: ReactNode;
	type?: "button" | "submit" | "reset";
	variant?: string;
	className?: string;
	onClick?: () => void;
};

export type EditorContentProps = {
	editor: {
		commands: {
			setContent: (content: string) => void;
			clearContent: (force?: boolean) => void;
		};
		getText: () => string;
	};
};

// EditorContentの型を更新
export type TipTapEditorProps = {
	editor: Editor;
};

// NotebookActionsの型定義
export type NotebookActionsType = {
	createNotebook: Mock;
	updateNotebook: Mock;
	getNotebooks: Mock;
	deleteNotebook: Mock;
};

// useFormの戻り値の型
export type FormFields = {
	title: FieldMetadata<string>;
	content: FieldMetadata<string>;
};
