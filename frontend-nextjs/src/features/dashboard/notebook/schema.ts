import { z } from "zod";

export const notebookSchema = z.object({
	title: z
		.string()
		.min(1, "タイトルは必須です")
		.max(200, "タイトルは200文字以内にしてください"),
	content: z.string().min(1, "本文は必須です"),
	user_id: z.string().optional(),
});
