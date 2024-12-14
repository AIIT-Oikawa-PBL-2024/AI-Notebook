import { useCallback } from "react";

const STORAGE_KEY = "noteInitialData";

interface NoteData {
	title: string;
	content: string;
}

export const useNoteInitialData = () => {
	// 初期データの保存
	const setInitialData = useCallback((data: NoteData) => {
		try {
			localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
		} catch (error) {
			console.error("Failed to save note initial data:", error);
		}
	}, []);

	// 初期データの取得と削除
	const getAndRemoveInitialData = useCallback((): NoteData | undefined => {
		try {
			const storedData = localStorage.getItem(STORAGE_KEY);
			if (!storedData) return undefined;

			localStorage.removeItem(STORAGE_KEY);
			return JSON.parse(storedData);
		} catch (error) {
			console.error("Failed to get note initial data:", error);
			return undefined;
		}
	}, []);

	return {
		setInitialData,
		getAndRemoveInitialData,
	};
};
