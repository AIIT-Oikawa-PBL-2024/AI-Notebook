import { useAuthFetch } from "@/hooks/useAuthFetch";
import { parseWithZod } from "@conform-to/zod";
import { getAuth } from "firebase/auth";
import { notebookSchema } from "../schema";
import type { Note } from "../types/data";

export function useNotebookActions() {
	const auth = getAuth();
	const currentUser = auth.currentUser;
	const authFetch = useAuthFetch();

	const getNotebooks = async (): Promise<Note[]> => {
		const endpoint = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/notes`;

		try {
			const response = await authFetch(endpoint);
			if (!response.ok) {
				throw new Error("リクエストに失敗しました");
			}
			return await response.json();
		} catch (error) {
			throw new Error("ノートブックの取得に失敗しました");
		}
	};

	const createNotebook = async (prevState: unknown, formData: FormData) => {
		const endpoint = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/notes`;

		if (currentUser) {
			// TODO: user id 仮置き
			formData.set("user_id", currentUser.uid);
		} else {
			throw new Error("ユーザー情報が取得できませんでした");
		}

		const submission = parseWithZod(formData, {
			schema: notebookSchema,
		});

		if (submission.status !== "success") {
			return submission.reply();
		}

		try {
			const response = await authFetch(endpoint, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(submission.value),
			});
			return await response.json();
		} catch (error) {
			throw new Error("ノートブックの作成に失敗しました");
		}
	};

	const updateNotebook = async (
		noteId: number,
		prevState: unknown,
		formData: FormData,
	) => {
		const endpoint = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/notes/${noteId}`;

		const submission = parseWithZod(formData, {
			schema: notebookSchema,
		});

		if (submission.status !== "success") {
			return submission.reply();
		}

		try {
			const response = await authFetch(endpoint, {
				method: "PUT",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(submission.value),
			});
			return await response.json();
		} catch (error) {
			throw new Error("ノートブックの更新に失敗しました");
		}
	};

	const deleteNotebook = async (noteId: number) => {
		const endpoint = `${process.env.NEXT_PUBLIC_BACKEND_HOST}/notes/${noteId}`;

		try {
			const response = await authFetch(endpoint, {
				method: "DELETE",
			});
			if (!response.ok) {
				throw new Error("リクエストに失敗しました");
			}
			return await response.json();
		} catch (error) {
			throw new Error("ノートブックの削除に失敗しました");
		}
	};
	return { getNotebooks, createNotebook, updateNotebook, deleteNotebook };
}
