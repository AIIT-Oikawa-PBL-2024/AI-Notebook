"use client";

import { useMultiChoiceQuestionGenerator } from "@/features/dashboard/ai-exercise/multiple-choice/useMultiChoiceQuestionGenerator";
import { useSaveAnswers } from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import type {
	AnswerResponseData,
	Question,
	SaveAnswerPayload,
} from "@/features/dashboard/ai-exercise/multiple-choice/useSaveAnswers";
import {
	Alert,
	Button,
	Card,
	CardBody,
	Radio,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useEffect, useState } from "react";

const ANSWERS_STORAGE_KEY = "cached_answers";
const RESULTS_STORAGE_KEY = "cached_results_state";

type ResultState = {
	showResults: boolean;
	retryMode: boolean;
	skippedQuestions: string[];
};

// 複数選択問題を表示し、ユーザーの回答を管理・送信するコンポーネント
export const MultipleChoiceQuestions = () => {
	const { loading, error, exercise, resetExercise, clearCache } =
		useMultiChoiceQuestionGenerator();

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
						skippedQuestions: [] as string[],
					};
		}
		return {
			showResults: false,
			retryMode: false,
			skippedQuestions: [] as string[],
		};
	});

	const { showResults, retryMode, skippedQuestions } = resultState;

	// useSaveAnswers フックを初期化
	const {
		saveAnswers,
		loading: saving,
		error: saveError,
		success,
	} = useSaveAnswers();

	// 選択した回答をローカルストレージに保存
	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(
				ANSWERS_STORAGE_KEY,
				JSON.stringify(selectedAnswers),
			);
		}
	}, [selectedAnswers]);

	// 結果状態をローカルストレージに保存
	useEffect(() => {
		if (typeof window !== "undefined") {
			localStorage.setItem(RESULTS_STORAGE_KEY, JSON.stringify(resultState));
		}
	}, [resultState]);

	if (loading) {
		return (
			<div
				className="flex h-screen items-center justify-center"
				aria-live="polite"
			>
				<Spinner className="h-8 w-8" aria-label="Loading spinner" role="img" />
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

	const questions: Question[] = exercise.content[0].input.questions;

	// 回答キャッシュをクリアします
	const clearAnswerCache = () => {
		localStorage.removeItem(ANSWERS_STORAGE_KEY);
		localStorage.removeItem(RESULTS_STORAGE_KEY);
		setSelectedAnswers({});
		setResultState({
			showResults: false,
			retryMode: false,
			skippedQuestions: [],
		});
	};

	// ユーザーの回答を選択します
	const handleAnswerSelect = (questionId: string, value: string) => {
		setSelectedAnswers((prev) => ({
			...prev,
			[questionId]: value,
		}));
	};

	// ユーザーの回答をバックエンドに送信して保存
	const handleSubmit = async () => {
		setResultState((prev) => ({
			...prev,
			showResults: true,
		}));
		// ページトップへスムーズにスクロール
		window.scrollTo({ top: 0, behavior: "smooth" });

		// 保存するデータを準備
		const title =
			typeof window !== "undefined" ? localStorage.getItem("title") || "" : "";
		const relatedFiles =
			typeof window !== "undefined"
				? JSON.parse(localStorage.getItem("selectedFiles") || "[]")
				: [];

		const responses: AnswerResponseData[] = questions.map((question) => {
			const userChoice = selectedAnswers[question.question_id];
			const isCorrect = userChoice === question.answer;
			return {
				question_id: question.question_id,
				question_text: question.question_text,
				choices: question.choices,
				user_selected_choice: userChoice,
				correct_choice: question.answer,
				is_correct: isCorrect,
				explanation: question.explanation, // 解説文を含める
			};
		});

		const payload: SaveAnswerPayload = {
			title,
			relatedFiles,
			responses,
		};

		// カスタムフックを使用して回答を保存
		await saveAnswers(payload);
	};

	// ユーザーの回答をリセット
	const handleReset = () => {
		clearAnswerCache();
		// ページトップへスムーズにスクロール
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	// 完全にリセットし、新しい問題を生成
	const handleCompleteReset = () => {
		clearCache();
		clearAnswerCache();
	};

	// 不正解のみをリトライ
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
		});
		resetExercise(); // ここで resetExercise を呼び出す
		window.scrollTo({ top: 0, behavior: "smooth" });
	};

	// スコアを計算
	const getScore = () => {
		return questions.reduce((score, question) => {
			return (
				score +
				(selectedAnswers[question.question_id] === question.answer ? 1 : 0)
			);
		}, 0);
	};

	// 選択肢のラベルを取得
	const getChoiceLabel = (question: Question, choiceId: string) => {
		return question.choices[choiceId as keyof typeof question.choices];
	};

	const displayQuestions = retryMode
		? questions.filter((q) => !skippedQuestions.includes(q.question_id))
		: questions;

	const title =
		typeof window !== "undefined" ? localStorage.getItem("title") : "";

	return (
		<div className="container mx-auto p-4 max-w-4xl">
			<div className="flex flex-col items-center mb-6">
				<Typography variant="h2" className="text-center">
					選択問題{retryMode ? "（復習モード）" : ""}
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
												checked={isUserChoice} // defaultCheckedからcheckedに変更
												label={
													<div className="flex items-center gap-2">
														<span
															className={
																showResults
																	? `${
																			isCorrectAnswer
																				? "text-green-700 font-semibold"
																				: ""
																		} ${
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
											className={`mb-2 ${
												isCorrect ? "text-blue-900" : "text-red-900"
											}`}
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

			{/* 保存中のステータスを表示 */}
			{saving && (
				<div className="flex items-center mb-4">
					<Spinner className="h-6 w-6" />
					<span className="ml-2">回答を保存中...</span>
				</div>
			)}
			{saveError && (
				<Alert color="red" className="mb-4">
					{saveError}
				</Alert>
			)}
			{success && (
				<Alert color="green" className="mb-4">
					回答が正常に保存されました。
				</Alert>
			)}

			<div className="flex justify-between items-center mt-6">
				{showResults ? (
					<div className="w-full flex justify-between items-center">
						<Typography variant="h5">
							スコア: {getScore()} / {displayQuestions.length}
						</Typography>
						<div className="flex gap-4">
							{!retryMode && getScore() !== questions.length && (
								<Button onClick={handleRetryIncorrect} color="amber">
									不正解のみやり直す
								</Button>
							)}
							<Button onClick={handleReset} color="blue">
								{retryMode ? "最初からやり直す" : "もう一度挑戦する"}
							</Button>
							<Button onClick={handleCompleteReset} color="red">
								新しい問題を生成
							</Button>
						</div>
					</div>
				) : (
					<Button
						onClick={handleSubmit}
						disabled={
							Object.keys(selectedAnswers).length !== displayQuestions.length ||
							saving // 保存中はボタンを無効化
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
