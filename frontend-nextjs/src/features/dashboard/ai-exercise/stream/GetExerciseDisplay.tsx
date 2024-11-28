"use client";

import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import {
	Alert,
	Card,
	CardBody,
	CardHeader,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useCallback, useEffect, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_EXERCISE = `${BACKEND_HOST}/exercises`;

interface Exercise {
	id: number;
	title: string;
	response: string;
	exercise_type: string;
	user_id: string;
	created_at: string;
}

type Props = {
	exerciseId: string;
};

export function GetExerciseDisplay({ exerciseId }: Props) {
	const [exercise, setExercise] = useState<Exercise | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	const { user } = useAuth();
	const authFetch = useAuthFetch();

	const fetchExercise = useCallback(async () => {
		if (!user || !exerciseId) {
			setError("認証が必要です");
			setLoading(false);
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(
				`${BACKEND_API_URL_GET_EXERCISE}/${exerciseId}`,
			);

			if (!response.ok) {
				throw new Error("練習問題の取得に失敗しました");
			}

			const data = await response.json();
			setExercise(data);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	}, [user, authFetch, exerciseId]);

	useEffect(() => {
		fetchExercise();
	}, [fetchExercise]);

	const tryParseJSON = (str: string): string => {
		try {
			const parsed = JSON.parse(str);
			if (typeof parsed === "object") {
				if (parsed.content?.[0]?.input?.questions) {
					const questions = parsed.content[0].input.questions;
					const questionTexts = questions.map(
						(q: { question_text: string }) => q.question_text,
					);
					return questionTexts.join("\n");
				}
				return JSON.stringify(parsed, null, 2);
			}
			return str;
		} catch (e) {
			return str;
		}
	};

	if (loading) {
		return (
			<div className="flex justify-center items-center min-h-screen">
				<Spinner
					role="progressbar"
					aria-label="Loading..."
					className="h-8 w-8"
				/>
			</div>
		);
	}

	if (error) {
		return (
			<div className="container mx-auto p-4">
				<Alert variant="gradient" color="red">
					{error}
				</Alert>
			</div>
		);
	}

	if (!exercise) {
		return (
			<div className="container mx-auto p-4">
				<Alert variant="gradient">練習問題が見つかりません</Alert>
			</div>
		);
	}

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<div className="flex flex-col items-center gap-2">
						<Typography variant="h3" className="text-gray-900">
							AI 練習問題
						</Typography>
						{exercise.title && (
							<Typography variant="h5" className="text-gray-700">
								{exercise.title}
							</Typography>
						)}
					</div>
				</CardHeader>
				<CardBody>
					<div className="whitespace-pre-wrap">
						{tryParseJSON(exercise.response)}
					</div>
				</CardBody>
			</Card>
		</div>
	);
}
