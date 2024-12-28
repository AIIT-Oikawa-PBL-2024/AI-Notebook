"use client";

import {
	Alert,
	Button,
	Card,
	CardBody,
	CardHeader,
	Radio,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

// 解答レスポンスの型定義
export interface AnswerResponse {
	id: number;
	title: string;
	related_files: string[];
	question_id: string;
	question_text: string;
	choice_a: string;
	choice_b: string;
	choice_c: string;
	choice_d: string;
	user_selected_choice?: "choice_a" | "choice_b" | "choice_c" | "choice_d"; // オプショナルなユニオン型
	correct_choice: "choice_a" | "choice_b" | "choice_c" | "choice_d"; // ユニオン型
	is_correct?: boolean; // オプショナル
	explanation: string;
	user_id: string;
	created_at: string; // ISO形式の文字列
	updated_at: string; // ISO形式の文字列
}

export default function SelectedAnswers() {
	const router = useRouter();
	const [selectedAnswers, setSelectedAnswers] = useState<
		AnswerResponse[] | null
	>(null);
	const [loading, setLoading] = useState<boolean>(true);
	const [error, setError] = useState<string>("");
	const [userSelections, setUserSelections] = useState<{
		[key: number]: string;
	}>({});

	// 各問題ごとに正解を確認したかどうかを追跡するための状態
	const [submittedAnswers, setSubmittedAnswers] = useState<Set<number>>(
		new Set(),
	);

	// 日付フォーマット関数
	const formatDate = (dateStr: string) => {
		return new Date(dateStr).toLocaleString();
	};

	// 選択肢IDをラベルに変換する関数
	const formatChoiceId = (choiceId: string): string => {
		const match = choiceId.match(/choice_([a-d])/i);
		if (match) {
			return match[1].toUpperCase();
		}
		return choiceId;
	};

	// 選択肢キーから選択肢テキストを取得するヘルパー関数
	const getChoiceText = (
		answer: AnswerResponse,
		choiceKey: "choice_a" | "choice_b" | "choice_c" | "choice_d",
	): string => {
		return answer[choiceKey];
	};

	// ページがロードされた時にローカルストレージからデータを読み込む
	useEffect(() => {
		try {
			const storedAnswers = localStorage.getItem("selectedAnswers");
			if (storedAnswers) {
				const parsedAnswers: AnswerResponse[] = JSON.parse(storedAnswers);
				setSelectedAnswers(parsedAnswers);
			} else {
				setError("選択された解答が見つかりません。");
			}
		} catch (err) {
			setError("データの読み込みに失敗しました。");
		} finally {
			setLoading(false);
		}
	}, []);

	// ユーザーの選択肢を処理
	const handleSelectionChange = (
		answerId: number,
		choice: "choice_a" | "choice_b" | "choice_c" | "choice_d",
	) => {
		setUserSelections((prev) => ({
			...prev,
			[answerId]: choice,
		}));
	};

	// 提出処理（個別の問題ごとに実行）
	const handleSubmit = (answerId: number) => {
		if (selectedAnswers) {
			const selectedChoice = userSelections[answerId] as
				| "choice_a"
				| "choice_b"
				| "choice_c"
				| "choice_d";
			const updatedAnswers = selectedAnswers.map((answer) => {
				if (answer.id === answerId) {
					return {
						...answer,
						is_correct: selectedChoice === answer.correct_choice,
						user_selected_choice: selectedChoice,
					};
				}
				return answer;
			});
			setSelectedAnswers(updatedAnswers);
			// 更新された選択肢をローカルストレージに保存（オプション）
			localStorage.setItem("selectedAnswers", JSON.stringify(updatedAnswers));
			// submittedAnswers にこの answerId を追加
			setSubmittedAnswers((prev) => new Set(prev).add(answerId));
		}
	};

	// リセット処理
	const handleReset = () => {
		setUserSelections({});
		setSubmittedAnswers(new Set());
		if (selectedAnswers) {
			const resetAnswers = selectedAnswers.map((answer) => ({
				...answer,
				is_correct: undefined, // オプショナルなため undefined を許容
				user_selected_choice: undefined, // オプショナルなため undefined を許容
			}));
			setSelectedAnswers(resetAnswers);
			localStorage.setItem("selectedAnswers", JSON.stringify(resetAnswers));
		}
	};

	// 解答がない場合の処理
	if (loading) {
		return (
			<div className="flex justify-center items-center h-screen">
				<Spinner className="h-8 w-8" />
				<span className="ml-2">選択された解答を読み込み中...</span>
			</div>
		);
	}

	if (error) {
		return (
			<div className="container mx-auto p-4">
				<Alert color="red" className="mb-4">
					{error}
				</Alert>
				<Button
					onClick={() => router.push("/ai-exercise/answers-list")}
					color="blue"
				>
					戻る
				</Button>
			</div>
		);
	}

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						問題に再チャレンジ
					</Typography>
				</CardHeader>
				<CardBody>
					{selectedAnswers && selectedAnswers.length > 0 ? (
						<form>
							{selectedAnswers.map((answer) => (
								<Card key={answer.id} className="mb-6 shadow-sm">
									<CardBody>
										<div className="flex justify-between items-center">
											<Typography variant="h5" className="font-semibold">
												{answer.title}
											</Typography>
										</div>
										<div className="mt-4">
											<Typography variant="h6" className="font-medium">
												問題:
											</Typography>
											<Typography className="whitespace-pre-wrap">
												{answer.question_text}
											</Typography>
										</div>
										<div className="mt-4">
											<Typography variant="h6" className="font-medium">
												選択肢:
											</Typography>
											<div className="flex flex-col space-y-2">
												{(
													[
														"choice_a",
														"choice_b",
														"choice_c",
														"choice_d",
													] as const
												).map((choiceKey) => {
													const choiceLabel = answer[choiceKey];
													const isCorrect = choiceKey === answer.correct_choice;
													const isUserChoice =
														userSelections[answer.id] === choiceKey;

													// 条件に応じたクラスを設定
													let labelClass = "text-gray-900"; // 通常のテキスト色
													if (submittedAnswers.has(answer.id)) {
														if (isCorrect) {
															labelClass = "text-green-900 font-semibold"; // 正解は緑色
														} else if (isUserChoice && !isCorrect) {
															labelClass = "text-red-900 font-semibold"; // ユーザーの誤答は赤色
														} else {
															labelClass = "text-gray-500"; // その他の選択肢は薄く
														}
													}

													return (
														<div key={choiceKey} className="flex items-center">
															<Radio
																id={`answer-${answer.id}-${choiceKey.charAt(
																	choiceKey.length - 1,
																)}`}
																label={
																	<span className={labelClass}>
																		{formatChoiceId(choiceKey)}. {choiceLabel}
																	</span>
																}
																name={`answer-${answer.id}`}
																value={choiceKey}
																checked={
																	userSelections[answer.id] === choiceKey
																}
																onChange={() =>
																	handleSelectionChange(answer.id, choiceKey)
																}
																color="blue"
																disabled={submittedAnswers.has(answer.id)}
															/>
															{/* 正解やユーザーの選択を表示 */}
															{submittedAnswers.has(answer.id) && (
																<>
																	{isCorrect && (
																		<span className="ml-2 text-green-700 font-semibold">
																			(正解)
																		</span>
																	)}
																	{isUserChoice && !isCorrect && (
																		<span className="ml-2 text-red-700 font-semibold">
																			(あなたの解答)
																		</span>
																	)}
																</>
															)}
														</div>
													);
												})}
											</div>
										</div>
										<div className="mt-4 flex justify-end">
											<Button
												type="button"
												onClick={() => handleSubmit(answer.id)}
												color="blue"
												disabled={
													submittedAnswers.has(answer.id) ||
													!userSelections[answer.id]
												}
											>
												正解を確認する
											</Button>
										</div>
										{submittedAnswers.has(answer.id) &&
											answer.is_correct !== undefined && (
												// 背景色を正誤に応じて変更
												<div
													className={`mt-4 p-4 rounded ${
														answer.is_correct ? "bg-blue-50" : "bg-pink-50"
													}`}
												>
													{answer.is_correct ? (
														<>
															<Alert color="green" className="mb-2">
																正解です！
															</Alert>
														</>
													) : (
														<>
															<Alert color="red" className="mb-2">
																不正解です。正しい答えは{" "}
																{formatChoiceId(answer.correct_choice)} です。
															</Alert>
														</>
													)}
													{/* ユーザーの解答を表示 */}
													<div className="mb-2">
														<Typography variant="h6" className="font-semibold">
															あなたの解答:
														</Typography>
														<Typography
															className={`whitespace-pre-wrap ${
																answer.is_correct
																	? "text-green-700"
																	: "text-red-700"
															}`}
														>
															{answer.user_selected_choice
																? formatChoiceId(answer.user_selected_choice)
																: "選択されていません"}
															.{" "}
															{answer.user_selected_choice
																? getChoiceText(
																		answer,
																		answer.user_selected_choice,
																	)
																: "選択されていません"}
														</Typography>
													</div>
													{/* 正解の解答を表示 */}
													<div className="mb-2">
														<Typography
															variant="h6"
															className="font-semibold text-green-700"
														>
															正解:
														</Typography>
														<Typography className="whitespace-pre-wrap text-green-700">
															{formatChoiceId(answer.correct_choice)}.{" "}
															{getChoiceText(answer, answer.correct_choice)}
														</Typography>
													</div>
													{/* 解説を表示 */}
													<div className="mt-2">
														<Typography variant="h6" className="font-semibold">
															解説:
														</Typography>
														<Typography className="whitespace-pre-wrap">
															{answer.explanation}
														</Typography>
													</div>
												</div>
											)}
									</CardBody>
								</Card>
							))}
							{/* リセットボタンをフォームの最後に追加 */}
							<div className="flex justify-end mt-4">
								<Button
									type="button"
									onClick={handleReset}
									color="gray"
									className="ml-4"
								>
									リセット
								</Button>
							</div>
						</form>
					) : (
						<Alert color="amber" className="mb-4">
							選択された解答が見つかりませんでした。
						</Alert>
					)}
				</CardBody>
			</Card>
		</div>
	);
}
