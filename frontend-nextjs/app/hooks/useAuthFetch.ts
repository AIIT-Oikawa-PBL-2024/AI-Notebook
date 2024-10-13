"use client";

import { useAuth } from "../components/AuthProvider";

export function useAuthFetch() {
	const { idToken } = useAuth();

	const authFetch = async (url: string, options: RequestInit = {}) => {
		if (!idToken) {
			throw new Error("認証されていません");
		}

		const headers = {
			...options.headers,
			Authorization: `Bearer ${idToken}`,
		};

		return fetch(url, {
			...options,
			headers,
		});
	};

	return authFetch;
}
