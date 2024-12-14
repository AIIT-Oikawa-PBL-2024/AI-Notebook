"use client";

import { useEssayQuestionGenerator } from "@/features/dashboard/ai-exercise/essay-question/useEssayQuestionGenerator";
import {
	Alert,
	Button,
	Card,
	CardBody,
	Spinner,
	Textarea,
	Typography,
} from "@material-tailwind/react";
import { useEffect, useState } from "react";

const ANSWERS_STORAGE_KEY = "cached_essay_answers";
const RESULTS_STORAGE_KEY = "cached_essay_results_state";

type ResultState = {
	showResults: boolean;
	retryMode: boolean;
	skippedQuestions: string[];
};

export const EssayQuestions = () => {
	const { loading, error, exercise, resetExercise, clearCache } =
		useEssayQuestionGenerator();

	const [answers, setAnswers] = useState<Record<string, string>>(() => {
		if (typeof window !== "undefined") {
			const cached = localStorage.getItem(ANSWERS_STORAGE_KEY);
			return cached ? JSON.parse(cached) : {};
		}
		return {};
	});

	const [resultState, setResultState] = useState<ResultState>(() => {
		if (typeof window !== "undefined") {
			const cached = localStorage.getItem(RESULTS_STORAGE_KEY);
			return cached
				? JSON.parse(cached)
				: {
						showResults: false,
						retryMode: false,
						skippedQuestions: [] as string[],
					};
		}
		return {
			showResults: false,
			retryMode: false,
			skippedQuestions: [] as string[],
		};
	});

	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(ANSWERS_STORAGE_KEY, JSON.stringify(answers));
		}
	}, [answers]);

	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(resultState));
		}
	}, [resultState]);

	const submitAnswersToBackend = async () => {
		/*
		try {
			const response = await fetch("/api/submit-answers", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ answers }),
			});
			const result = await response.json();
			setResultState((prev) => ({
				...prev,
				showResults: true,
			}));
			console.log("Backend response:", result);
		} catch (error) {
			console.error("Error submitting answers:", error);
		}
		// */
	};

	if (loading) {
		return (
			<div className="flex h-screen items-center justify-center">
				<Spinner className="h-8 w-8" />
				<span className="ml-2">問題を生成中...</span>
			</div>
		);
	}

	if (error) {
		return (
			<div className="container mx-auto p-4">
				<Alert color="red" className="mb-4">
					エラーが発生しました: {error}
				</Alert>
				<div className="flex gap-4">
					<Button onClick={resetExercise} color="gray">
						再試行
					</Button>
					<Button onClick={clearCache} color="gray">
						キャッシュをクリア
					</Button>
				</div>
			</div>
		);
	}

	if (!exercise?.content[0]?.input?.questions) {
		return (
			<div className="container mx-auto p-4">
				<Alert color="amber" className="mb-4">
					問題が見つかりません。もう一度お試しください。
				</Alert>
				<div className="flex gap-4">
					<Button onClick={resetExercise} color="gray">
						再試行
					</Button>
					<Button onClick={clearCache} color="gray">
						キャッシュをクリア
					</Button>
				</div>
			</div>
		);
	}

	const questions = exercise.content[0].input.questions;

	const handleAnswerChange = (questionId: string, value: string) => {
		setAnswers((prev) => ({
			...prev,
			[questionId]: value,
		}));
	};

	const handleSubmit = () => {
		submitAnswersToBackend();
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	const handleReset = () => {
		setAnswers({});
		setResultState({
			showResults: false,
			retryMode: false,
			skippedQuestions: [],
		});
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	return (
		<div className="container mx-auto p-4 max-w-4xl">
			<Typography variant="h2" className="text-center mb-6">
				記述問題
			</Typography>
			{questions.map((question, index) => (
				<Card key={question.question_id} className="mb-6 shadow-sm">
					<CardBody>
						<Typography variant="h6" className="mb-4">
							問題 {index + 1}. {question.question_text}
						</Typography>
						<Textarea
							placeholder="ここに回答を入力してください"
							value={answers[question.question_id] || ""}
							onChange={(e) =>
								handleAnswerChange(question.question_id, e.target.value)
							}
							disabled={resultState.showResults}
						/>
						{resultState.showResults && (
							<div className="mt-4">
								<Typography className="text-gray-900">あなたの回答:</Typography>
								<Typography className="text-blue-900">
									{answers[question.question_id] || "未回答"}
								</Typography>
							</div>
						)}
					</CardBody>
				</Card>
			))}
			<div className="flex justify-between items-center mt-6">
				{resultState.showResults ? (
					<div className="w-full flex justify-between items-center">
						<Typography variant="h5">結果を確認してください</Typography>
						<Button onClick={handleReset} color="blue">
							もう一度挑戦する
						</Button>
					</div>
				) : (
					<Button
						onClick={handleSubmit}
						disabled={Object.keys(answers).length !== questions.length}
						color="blue"
					>
						回答を送信する
					</Button>
				)}
			</div>
		</div>
	);
};
