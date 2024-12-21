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
import ReactMarkdown from "react-markdown";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_OUTPUT = `${BACKEND_HOST}/outputs`;

interface Output {
	id: number;
	title: string;
	output: string;
	user_id: string;
	created_at: string;
}

type Props = {
	outputId: string;
};

export function GetAIOutputDisplay({ outputId }: Props) {
	const [output, setOutput] = useState<Output | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	const { user } = useAuth();
	const authFetch = useAuthFetch();

	const fetchOutput = useCallback(async () => {
		if (!user || !outputId) {
			setError("認証が必要です");
			setLoading(false);
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(
				`${BACKEND_API_URL_GET_OUTPUT}/${outputId}`,
			);

			if (!response.ok) {
				throw new Error("AI要約の取得に失敗しました");
			}

			const data = await response.json();
			setOutput(data);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	}, [user, authFetch, outputId]);

	useEffect(() => {
		fetchOutput();
	}, [fetchOutput]);

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

	if (!output) {
		return (
			<div className="container mx-auto p-4">
				<Alert variant="gradient">AI要約が見つかりません</Alert>
			</div>
		);
	}

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<div className="flex flex-col items-center gap-2">
						<Typography variant="h3" className="text-gray-900">
							AI 出力
						</Typography>
						{output.title && (
							<Typography variant="h5" className="text-gray-700">
								{output.title}
							</Typography>
						)}
					</div>
				</CardHeader>
				<CardBody>
					<div className="prose max-w-none">
						{loading && (
							<div className="flex justify-center p-4">
								<Spinner className="h-8 w-8" />
							</div>
						)}
						{output && (
							<ReactMarkdown
								components={{
									h1: ({ node, ...props }) => (
										<h1 className="text-2xl font-bold mb-4" {...props} />
									),
									h2: ({ node, ...props }) => (
										<h2 className="text-xl font-bold mb-3" {...props} />
									),
									p: ({ node, ...props }) => <p className="mb-4" {...props} />,
									ul: ({ node, ...props }) => (
										<ul className="list-disc pl-6 mb-4" {...props} />
									),
									ol: ({ node, ...props }) => (
										<ol className="list-decimal pl-6 mb-4" {...props} />
									),
								}}
							>
								{output.output}
							</ReactMarkdown>
						)}
					</div>
				</CardBody>
			</Card>
		</div>
	);
}
