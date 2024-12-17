"use client";

import { useEssayQuestionGenerator } from "@/features/dashboard/ai-exercise/essay-question/useEssayQuestionGenerator";
import { useSubmitAnswers } from "@/features/dashboard/ai-exercise/essay-question/useSubmitAnswers";
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

const formatAnswersForRequest = (
	answers: Record<string, string>,
	questions: {
		question_id: string;
		question_text: string;
		answer?: string;
		explanation?: string;
	}[],
	exercise_id: number,
) => {
	// 質問データを整形
	const formattedQuestions = questions.map((question) => ({
		question_id: question.question_id,
		question_text: question.question_text,
		user_answer: answers[question.question_id] || "",
		answer: question.answer || "",
		explanation: question.explanation || "",
	}));

	// JSON文字列として answer に含める
	const answer = JSON.stringify({
		questions: formattedQuestions,
	});

	// 現在のタイムスタンプを取得
	const createdAt = new Date().toISOString();

	// リクエストフォーマットを返却
	return {
		answer, // JSON文字列
		scoring_results: "", // 空文字列を仮設定
		exercise_id, // 数値で送信
		created_at: createdAt, // ISO 8601形式のタイムスタンプ
	};
};

export const EssayQuestions = () => {
	const { loading, error, exercise, resetExercise, clearCache } =
		useEssayQuestionGenerator();

	const {
		isSubmitting,
		error: submitError,
		submitAnswers,
	} = useSubmitAnswers();

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

	const handleAnswerChange = (questionId: string, value: string) => {
		setAnswers((prev) => ({
			...prev,
			[questionId]: value,
		}));
	};

	const handleSubmit = async () => {
		try {
			if (!exercise) {
				console.error("Exercise data is not available.");
				return;
			}
			const formattedRequest = formatAnswersForRequest(
				answers,
				exercise.content[0].input.questions,
				exercise.exercise_id, // exercise_id を追加
			);
			const result = await submitAnswers(formattedRequest);
			setResultState((prev) => ({
				...prev,
				showResults: true,
			}));
			console.log("Backend response:", result);
		} catch (err) {
			console.error("Error submitting answers:", err);
		}
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
			{submitError && (
				<Alert color="red" className="mt-4">
					エラーが発生しました: {submitError}
				</Alert>
			)}
		</div>
	);
};
