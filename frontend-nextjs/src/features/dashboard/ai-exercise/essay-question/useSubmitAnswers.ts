import { useState } from "react";
import { useAuthFetch } from "@/hooks/useAuthFetch";

export const useSubmitAnswers = () => {
	const [isSubmitting, setIsSubmitting] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const authFetch = useAuthFetch();

	const submitAnswers = async (data: Record<string, unknown>) => {
		setIsSubmitting(true);
		setError(null);

		try {
			const response = await authFetch(
				`${process.env.NEXT_PUBLIC_BACKEND_HOST}/exercises/user_answer`,
				{
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ data }),
				},
			);

			if (!response.ok) {
				throw new Error(`Error: ${response.statusText}`);
			}

			const result = await response.json();
			return result;
		} catch (err: unknown) {
			if (err instanceof Error) {
				setError(err.message);
			} else {
				setError("An error occurred");
			}
			throw err;
		} finally {
			setIsSubmitting(false);
		}
	};

	return { isSubmitting, error, submitAnswers };
};
