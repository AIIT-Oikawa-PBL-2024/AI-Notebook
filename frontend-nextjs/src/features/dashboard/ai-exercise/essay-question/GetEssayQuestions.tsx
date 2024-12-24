"use client";

import { useGetEssayQuestion } from "@/features/dashboard/ai-exercise/essay-question/useGetEssayQuestion";
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
	scoringDetails: {
		question_id: string;
		scoring_result: string;
		explanation: string;
		answer: string; // 回答例を追加
	}[];
};

type ScoringResult = {
	question_id: string;
	scoring_result: string;
	explanation: string;
};

interface Props {
	exerciseId?: string;
}

const formatAnswersForRequest = (
	answers: Record<string, string>,
	exercise_id: number,
) => {
	const user_answer = Object.values(answers);
	return {
		exercise_id,
		user_answer,
	};
};

export const GetEssayQuestions = ({ exerciseId }: Props) => {
	const {
		loading,
		error,
		exercise,
		parsedResponse,
		resetExercise,
		clearCache,
	} = useGetEssayQuestion(exerciseId);

	const { error: submitError, submitAnswers } = useSubmitAnswers();

	const [isSubmitting, setIsSubmitting] = useState(false);

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
						scoringDetails: [], // 初期値を空配列に設定
					};
		}
		return {
			showResults: false,
			retryMode: false,
			skippedQuestions: [] as string[],
			scoringDetails: [],
		};
	});

	const [scoringResults, setScoringResults] = useState<ScoringResult[]>([]);

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

	if (
		!exercise ||
		!parsedResponse ||
		!parsedResponse.content?.[0]?.input?.questions
	) {
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

	const questions = parsedResponse.content[0].input.questions;
	const title = exercise.title;

	const handleAnswerChange = (questionId: string, value: string) => {
		setAnswers((prev) => ({
			...prev,
			[questionId]: value,
		}));
	};

	const handleSubmit = async () => {
		try {
			setIsSubmitting(true); // 送信中フラグをオン
			if (!exercise) {
				console.error("Exercise data is not available.");
				return;
			}
			const formattedRequest = formatAnswersForRequest(answers, exercise.id);
			const result = await submitAnswers(formattedRequest);

			const parsedResults = JSON.parse(result.scoring_results);
			const scoringDetails = parsedResults.content[0]?.input?.questions?.map(
				(q: {
					question_id: string;
					scoring_result: string;
					explanation: string;
				}) => ({
					question_id: q.question_id,
					scoring_result: q.scoring_result,
					explanation: q.explanation,
					answer:
						questions.find((item) => item.question_id === q.question_id)
							?.answer || "", // 回答例をマッピング
				}),
			);

			const newResultState = {
				...resultState,
				showResults: true,
				scoringDetails,
			};

			setResultState(newResultState);
			localStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(newResultState));
		} catch (err) {
			console.error("Error submitting answers:", err);
		} finally {
			setIsSubmitting(false); // 送信中フラグをオフ
		}
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	const handleReset = () => {
		setAnswers({});
		setResultState({
			showResults: false,
			retryMode: false,
			skippedQuestions: [],
			scoringDetails: [],
		});
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	return (
		<div className="container mx-auto p-4 max-w-4xl">
			<div className="flex flex-col items-center mb-6">
				<Typography variant="h2" className="text-center">
					記述問題
				</Typography>
				{title && (
					<Typography variant="h4" className="text-gray-700 mt-2">
						{title}
					</Typography>
				)}
			</div>

			{questions.map((question, index) => {
				const result = resultState.scoringDetails.find(
					(r) => r.question_id === question.question_id,
				);

				return (
					<Card key={question.question_id} className="mb-6 shadow-sm">
						<CardBody>
							<Typography variant="h6" className="mb-4">
								問題 {index + 1}. {question.question_text}
							</Typography>
							<Textarea
								className="mt-1 focus:outline-none !border !border-gray-300 focus:!border-gray-900 rounded-lg"
								labelProps={{
									className: "before:content-none after:content-none",
								}}
								placeholder="ここに回答を入力してください"
								value={answers[question.question_id] || ""}
								onChange={(e) =>
									handleAnswerChange(question.question_id, e.target.value)
								}
								disabled={resultState.showResults}
							/>
							{resultState.showResults && result && (
								<div className="mt-4">
									<Typography className="text-blue-900">
										採点結果: {result.scoring_result}
									</Typography>
									<Typography className="text-blue-700">
										理由: {result.explanation}
									</Typography>
									<Typography className="text-green-700 mt-2">
										回答例: {result.answer || "回答例はありません"}
									</Typography>
								</div>
							)}
						</CardBody>
					</Card>
				);
			})}

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
						{isSubmitting ? "送信中..." : "回答を送信する"}
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
