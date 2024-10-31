"use client";

import {
	Alert,
	Card,
	CardBody,
	CardHeader,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import ReactMarkdown from "react-markdown";

interface ExerciseDisplayProps {
	loading: boolean;
	error: string;
	exercise: string;
}

export function ExerciseDisplay({
	loading,
	error,
	exercise,
}: ExerciseDisplayProps) {
	return (
		<Card className="w-full">
			<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
				<Typography variant="h3" className="text-gray-900">
					AI 練習問題
				</Typography>
			</CardHeader>
			<CardBody className="flex flex-col gap-4">
				{loading && (
					<div className="flex justify-center p-4">
						<Spinner className="h-8 w-8" />
					</div>
				)}

				{error && (
					<Alert color="red" variant="gradient">
						{error}
					</Alert>
				)}

				{exercise && (
					<div className="prose max-w-none">
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
							{exercise}
						</ReactMarkdown>
					</div>
				)}
			</CardBody>
		</Card>
	);
}
