import { useAuth } from "@/providers/AuthProvider";
import { useCallback, useRef } from "react";

export function useAuthFetch() {
	const { idToken } = useAuth();
	const timeoutRef = useRef<NodeJS.Timeout>();

	const authFetch = useCallback(
		async (url: string, options: RequestInit = {}) => {
			if (!idToken) {
				throw new Error("認証されていません");
			}

			return new Promise<Response>((resolve, reject) => {
				if (timeoutRef.current) {
					clearTimeout(timeoutRef.current);
				}

				timeoutRef.current = setTimeout(async () => {
					try {
						const headers = {
							...options.headers,
							Authorization: `Bearer ${idToken}`,
						};

						const response = await fetch(url, {
							...options,
							headers,
						});
						resolve(response);
					} catch (error) {
						reject(error);
					}
				}, 300);
			});
		},
		[idToken],
	);

	return authFetch;
}
