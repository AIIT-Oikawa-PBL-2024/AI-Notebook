"use client";

import { Toaster } from "@/components/elements/Toaster";
import { useGetMultiChoiceQuestion } from "@/features/dashboard/ai-exercise/multiple-choice/useGetMultiChoiceQuestion";
import { useMakeSimilarQuestions } from "@/features/dashboard/ai-exercise/multiple-choice/useMakeSimilarQuestions";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import {
	Alert,
	Button,
	Card,
	CardBody,
	Radio,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import React, { useEffect, useState } from "react";

const ANSWERS_STORAGE_KEY = "cached_answers";
const RESULTS_STORAGE_KEY = "cached_results_state";

type ResultState = {
	showResults: boolean;
	retryMode: boolean;
	skippedQuestions: string[];
	showingSimilarQuestions: boolean;
};

interface Props {
	exerciseId?: string;
}

interface RelatedFile {
	file_name: string;
	file_size: number;
	id: number;
	user_id: string;
	created_at: string;
}

export const GetMultipleChoiceQuestions = ({ exerciseId }: Props) => {
	const {
		loading: originalLoading,
		error: originalError,
		exercise: originalExercise,
		parsedResponse: originalParsedResponse,
		resetExercise,
		clearCache,
	} = useGetMultiChoiceQuestion(exerciseId);

	const {
		similarQuestions,
		loading: similarLoading,
		error: similarError,
		exercise: similarExercise,
	} = useMakeSimilarQuestions();

	const {
		saveAnswers,
		loading: saving,
		error: saveError,
		success,
	} = useSaveAnswers();

	const [similarQuestionsLoading, setSimilarQuestionsLoading] = useState(false);

	const [selectedAnswers, setSelectedAnswers] = useState<
		Record<string, string>
	>(() => {
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
						skippedQuestions: [],
						showingSimilarQuestions: false,
					};
		}
		return {
			showResults: false,
			retryMode: false,
			skippedQuestions: [],
			showingSimilarQuestions: false,
		};
	});

	const { showResults, retryMode, skippedQuestions, showingSimilarQuestions } =
		resultState;

	const loading = originalLoading || similarLoading;
	const error = originalError || similarError;
	const exercise = showingSimilarQuestions ? similarExercise : originalExercise;
	const parsedResponse = showingSimilarQuestions
		? similarExercise
		: originalParsedResponse;

	useEffect(() => {
		if (success) {
			Toaster({
				message: "解答が正常に保存されました。",
				type: "success",
			});
		}
	}, [success]);

	useEffect(() => {
		if (saveError) {
			Toaster({
				message: "解答の保存中にエラーが発生しました",
				type: "warning",
			});
		}
	}, [saveError]);

	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(
				ANSWERS_STORAGE_KEY,
				JSON.stringify(selectedAnswers),
			);
		}
	}, [selectedAnswers]);

	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(resultState));
		}
	}, [resultState]);

	useEffect(() => {
		console.log(
			"コンポーネントマウント時の selectedFiles:",
			localStorage.getItem("selectedFiles"),
		);
	}, []);

	if (loading || similarQuestionsLoading) {
		return (
			<div
				className="flex h-screen items-center justify-center"
				aria-live="polite"
			>
				<Spinner className="h-8 w-8" aria-label="Loading spinner" role="img" />
				<span className="ml-2">
					{similarQuestionsLoading ? "類似問題を生成中..." : "問題を生成中..."}
				</span>
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
	const title = "title" in exercise ? exercise.title : undefined;

	const clearAnswerCache = () => {
		localStorage.removeItem(ANSWERS_STORAGE_KEY);
		localStorage.removeItem(RESULTS_STORAGE_KEY);
		setSelectedAnswers({});
		setResultState({
			showResults: false,
			retryMode: false,
			skippedQuestions: [],
			showingSimilarQuestions: false,
		});
	};

	const handleAnswerSelect = (questionId: string, value: string) => {
		setSelectedAnswers((prev) => ({
			...prev,
			[questionId]: value,
		}));
	};

	const handleGenerateSimilarQuestions = async () => {
		const incorrectResponses = questions
			.filter(
				(question) => selectedAnswers[question.question_id] !== question.answer,
			)
			.map((question) => ({
				question_id: question.question_id,
				question_text: question.question_text,
				choices: question.choices,
				user_selected_choice: selectedAnswers[question.question_id],
				correct_choice: question.answer,
				is_correct: false,
				explanation: question.explanation,
			}));

		if (incorrectResponses.length === 0) {
			Toaster({
				message: "不正解の問題がありません。",
				type: "warning",
			});
			return;
		}

		setSimilarQuestionsLoading(true);
		try {
			// 元の問題のタイトルを使用（ない場合は空文字）
			const originalTitle = "title" in exercise ? exercise.title : "";
			// タイトルに「（類似問題）」を付加
			const similarTitle = `${originalTitle}（類似問題）`;

			// 元の問題の関連ファイルを使用
			const relatedFiles =
				typeof window !== "undefined"
					? JSON.parse(localStorage.getItem("selectedFiles") || "[]")
					: [];

			const payload = {
				title: similarTitle,
				relatedFiles: relatedFiles.map((file: RelatedFile) => file.file_name),
				responses: incorrectResponses,
			};

			await similarQuestions(payload);
			setResultState((prev) => ({
				...prev,
				showingSimilarQuestions: true,
				showResults: false,
			}));
			setSelectedAnswers({});
			window.scrollTo({ top: 0, behavior: "smooth" });
		} catch (error) {
			Toaster({
				message: "類似問題の生成中にエラーが発生しました",
				type: "error",
			});
		} finally {
			setSimilarQuestionsLoading(false);
		}
	};

	const handleSubmit = async () => {
		setResultState((prev) => ({
			...prev,
			showResults: true,
		}));

		window.scrollTo({ top: 0, behavior: "smooth" });

		const responses = questions.map((question) => {
			const userChoice = selectedAnswers[question.question_id];
			const isCorrect = userChoice === question.answer;
			return {
				question_id: question.question_id,
				question_text: question.question_text,
				choices: question.choices,
				user_selected_choice: userChoice,
				correct_choice: question.answer,
				is_correct: isCorrect,
				explanation: question.explanation,
			};
		});

		// ローカルストレージから直接titleとrelatedFilesを取得
		const savedTitle = localStorage.getItem("title");
		// 元の問題の関連ファイルを使用
		const relatedFiles =
			typeof window !== "undefined"
				? JSON.parse(localStorage.getItem("selectedFiles") || "[]")
				: [];
		console.log("取得した relatedFiles:", relatedFiles);
		console.log(
			"localStorage の selectedFiles:",
			localStorage.getItem("selectedFiles"),
		);

		const payload = {
			title: savedTitle || "",
			relatedFiles: relatedFiles.map((file: RelatedFile) => file.file_name),
			responses: responses,
		};

		console.log("送信するペイロード:", payload);
		try {
			await saveAnswers(payload);
		} catch (error) {
			console.error("保存時のエラー詳細:", error);
		}
	};

	const handleReset = () => {
		clearAnswerCache();
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	const handleRetryIncorrect = () => {
		const correctQuestions = questions
			.filter(
				(question) => selectedAnswers[question.question_id] === question.answer,
			)
			.map((q) => q.question_id);

		setSelectedAnswers({});
		setResultState({
			showResults: false,
			retryMode: true,
			skippedQuestions: correctQuestions,
			showingSimilarQuestions: false,
		});
		resetExercise();
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	const getScore = () => {
		return questions.reduce((score, question) => {
			return (
				score +
				(selectedAnswers[question.question_id] === question.answer ? 1 : 0)
			);
		}, 0);
	};

	const getChoiceLabel = (
		question: (typeof questions)[0],
		choiceId: string,
	) => {
		return question.choices[choiceId as keyof typeof question.choices];
	};

	const displayQuestions = retryMode
		? questions.filter((q) => !skippedQuestions.includes(q.question_id))
		: questions;

	return (
		<div className="container mx-auto p-4 max-w-4xl">
			<div className="flex flex-col items-center mb-6">
				<Typography variant="h2" className="text-center">
					選択問題
					{retryMode ? "（復習モード）" : ""}
					{showingSimilarQuestions ? "（類似問題）" : ""}
				</Typography>
				{title && (
					<Typography variant="h4" className="text-gray-700 mt-2">
						{title}
					</Typography>
				)}
			</div>

			{displayQuestions.map((question, index) => {
				const isCorrect =
					selectedAnswers[question.question_id] === question.answer;
				return (
					<Card key={question.question_id} className="mb-6 shadow-sm">
						<CardBody>
							<Typography variant="h6" className="mb-4">
								問題 {retryMode ? "復習-" : ""}
								{index + 1}. {question.question_text}
							</Typography>

							<div className="space-y-2">
								{Object.entries(question.choices).map(([key, value]) => {
									const isUserChoice =
										selectedAnswers[question.question_id] === key;
									const isCorrectAnswer = key === question.answer;
									return (
										<div key={key} className="flex items-center">
											<Radio
												name={question.question_id}
												value={key}
												onChange={() =>
													handleAnswerSelect(question.question_id, key)
												}
												disabled={showResults}
												checked={isUserChoice}
												label={
													<div className="flex items-center gap-2">
														<span
															className={
																showResults
																	? `${isCorrectAnswer ? "text-green-700 font-semibold" : ""} ${
																			isUserChoice
																				? "font-semibold text-gray-900"
																				: "text-gray-600"
																		}`
																	: ""
															}
														>
															{value}
														</span>
														{showResults && (
															<>
																{isCorrectAnswer && (
																	<span className="text-green-700 font-medium ml-2">
																		(正解)
																	</span>
																)}
																{isUserChoice && !isCorrectAnswer && (
																	<span className="text-red-700 font-medium ml-2">
																		(あなたの解答)
																	</span>
																)}
															</>
														)}
													</div>
												}
												className={
													showResults && isCorrectAnswer ? "text-green-700" : ""
												}
											/>
										</div>
									);
								})}
							</div>

							{showResults && (
								<div className="mt-4">
									<div
										className={`p-4 rounded-lg ${
											isCorrect
												? "bg-blue-50"
												: "bg-red-50 border border-red-100"
										}`}
									>
										<div className="flex gap-2 mb-2">
											<Typography className="text-gray-900">
												あなたの解答:
											</Typography>
											<Typography
												className={
													isCorrect
														? "text-green-700 font-medium"
														: "text-red-700 font-medium"
												}
											>
												{getChoiceLabel(
													question,
													selectedAnswers[question.question_id],
												)}
											</Typography>
										</div>
										<div className="flex gap-2 mb-4">
											<Typography className="text-gray-900">正解:</Typography>
											<Typography className="text-green-700 font-medium">
												{getChoiceLabel(question, question.answer)}
											</Typography>
										</div>
										<Typography
											variant="h6"
											className={`mb-2 ${isCorrect ? "text-blue-900" : "text-red-900"}`}
										>
											解説:
										</Typography>
										<Typography className="text-gray-900">
											{question.explanation}
										</Typography>
									</div>
								</div>
							)}
						</CardBody>
					</Card>
				);
			})}

			{saving && (
				<div className="flex items-center mb-4">
					<Spinner className="h-6 w-6" />
					<span className="ml-2">解答を保存中...</span>
				</div>
			)}

			<div className="flex justify-between items-center mt-6">
				{showResults ? (
					<div className="w-full flex justify-between items-center">
						<Typography variant="h5">
							スコア: {getScore()} / {displayQuestions.length}
						</Typography>
						<div className="flex gap-4">
							{!retryMode &&
								!showingSimilarQuestions &&
								getScore() !== questions.length && (
									<>
										<Button
											onClick={handleGenerateSimilarQuestions}
											color="deep-orange"
										>
											不正解の類似問題を生成
										</Button>
										<Button onClick={handleRetryIncorrect} color="amber">
											不正解のみやり直す
										</Button>
									</>
								)}
							<Button onClick={handleReset} color="blue">
								{retryMode ? "最初からやり直す" : "もう一度挑戦する"}
							</Button>
						</div>
					</div>
				) : (
					<Button
						// 非同期にして保存中はボタンを無効化
						onClick={handleSubmit}
						disabled={
							Object.keys(selectedAnswers).length !== displayQuestions.length ||
							saving
						}
						color="blue"
						className="ml-auto"
					>
						正解を確認する
					</Button>
				)}
			</div>
		</div>
	);
};
