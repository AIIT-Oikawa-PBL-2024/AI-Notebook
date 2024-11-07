import { useOutputGenerator } from "@/features/dashboard/ai-output/hooks/useOutputGenerator";
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Mock useAuthFetch
vi.mock("@/hooks/useAuthFetch", () => ({
	useAuthFetch: () =>
		vi.fn(async () => ({
			ok: true,
			body: {
				getReader: () => ({
					read: vi
						.fn()
						.mockResolvedValueOnce({
							done: false,
							value: new TextEncoder().encode("test"),
						})
						.mockResolvedValueOnce({ done: true }),
				}),
			},
		})),
}));

// Mock localStorage
const localStorageMock = (() => {
	let store: { [key: string]: string } = {};
	return {
		getItem: (key: string) => store[key] || null,
		setItem: (key: string, value: string) => {
			store[key] = value;
		},
		removeItem: (key: string) => {
			delete store[key];
		},
		clear: () => {
			store = {};
		},
	};
})();

Object.defineProperty(window, "localStorage", { value: localStorageMock });

describe("useOutputGenerator", () => {
	beforeEach(() => {
		localStorage.clear();
		vi.clearAllMocks();
	});

	it("should handle streaming data", async () => {
		const { result } = renderHook(() => useOutputGenerator());

		await act(async () => {
			await new Promise((resolve) => setTimeout(resolve, 0));
		});

		expect(result.current.output).toBe("test");
		expect(result.current.loading).toBe(false);
	});
});
