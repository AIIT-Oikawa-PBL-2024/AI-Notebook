import { useNoteInitialData } from "@/features/dashboard/ai-output/select-ai-output/useNoteInitialData";
import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

describe("useNoteInitialData", () => {
	// localStorageのモック
	const mockLocalStorage = {
		getItem: vi.fn(),
		setItem: vi.fn(),
		removeItem: vi.fn(),
	};

	// テストデータ
	const testData = {
		title: "テストタイトル",
		content: "テスト本文",
	};

	beforeEach(() => {
		// テストごとにモックをリセット
		vi.clearAllMocks();
		// グローバルのlocalStorageをモックに置き換え
		Object.defineProperty(window, "localStorage", {
			value: mockLocalStorage,
		});
	});

	it("初期データを正しく保存できること", () => {
		const { result } = renderHook(() => useNoteInitialData());

		result.current.setInitialData(testData);

		expect(mockLocalStorage.setItem).toHaveBeenCalledTimes(1);
		expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
			"noteInitialData",
			JSON.stringify(testData),
		);
	});

	it("保存されたデータを取得して削除できること", () => {
		// 保存されたデータをモック
		mockLocalStorage.getItem.mockReturnValue(JSON.stringify(testData));

		const { result } = renderHook(() => useNoteInitialData());
		const retrievedData = result.current.getAndRemoveInitialData();

		expect(retrievedData).toEqual(testData);
		expect(mockLocalStorage.getItem).toHaveBeenCalledTimes(1);
		expect(mockLocalStorage.removeItem).toHaveBeenCalledTimes(1);
		expect(mockLocalStorage.removeItem).toHaveBeenCalledWith("noteInitialData");
	});

	it("保存されたデータがない場合はundefinedを返すこと", () => {
		mockLocalStorage.getItem.mockReturnValue(null);

		const { result } = renderHook(() => useNoteInitialData());
		const retrievedData = result.current.getAndRemoveInitialData();

		expect(retrievedData).toBeUndefined();
		expect(mockLocalStorage.removeItem).not.toHaveBeenCalled();
	});

	it("localStorageでエラーが発生した場合は適切にハンドリングされること", () => {
		// コンソールエラーをモック化
		const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

		// setItemでエラーを発生させる
		mockLocalStorage.setItem.mockImplementation(() => {
			throw new Error("Storage error");
		});

		const { result } = renderHook(() => useNoteInitialData());

		// エラーがスローされずにハンドリングされることを確認
		expect(() => result.current.setInitialData(testData)).not.toThrow();
		expect(consoleSpy).toHaveBeenCalled();

		consoleSpy.mockRestore();
	});
});
