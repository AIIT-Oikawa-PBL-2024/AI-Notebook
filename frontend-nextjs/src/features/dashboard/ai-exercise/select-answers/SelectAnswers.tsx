"use client";

import { PopupDialog } from "@/components/elements/PopupDialog";
import { useDeleteAnswers } from "@/features/dashboard/ai-exercise/select-answers/useDeleteAnswers";
import {
	type AnswerResponse,
	useFetchAnswers,
} from "@/features/dashboard/ai-exercise/select-answers/useFetchAnswers";
import {
	Alert,
	Button,
	Card,
	CardBody,
	CardHeader,
	Checkbox,
	Dialog,
	DialogBody,
	DialogHeader,
	Input,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AnswersTable } from "./AnswersTable"; // AnswersTableコンポーネントをインポート

// クリアすべきローカルストレージキーの定義
const STORAGE_KEYS_TO_CLEAR = [
	"cached_answers",
	"cached_results_state",
	"cached_multi_choice_question",
	"multi_choice_generation_status",
	"cached_essay_answers",
	"cached_essay_results_state",
];

export default function SelectAnswers() {
	const router = useRouter();

	// ▼ ページネーション対応の State / 関数を取得
	const {
		answers,
		loading,
		error,
		refetch,
		// ページネーション用
		totalCount,
		currentPage,
		totalPages,
	} = useFetchAnswers();

	const [selectedAnswerIds, setSelectedAnswerIds] = useState<number[]>([]);
	const [searchTerm, setSearchTerm] = useState<string>("");
	const [debouncedSearchTerm, setDebouncedSearchTerm] = useState<string>("");
	const [sortConfig, setSortConfig] = useState<{
		field: keyof AnswerResponse;
		direction: "asc" | "desc";
	}>({
		field: "updated_at",
		direction: "desc",
	});
	const [openModal, setOpenModal] = useState<boolean>(false);
	const [selectedAnswer, setSelectedAnswer] = useState<AnswerResponse | null>(
		null,
	);

	const {
		deleteAnswers,
		loading: deleting,
		error: deleteError,
	} = useDeleteAnswers();

	// ▼ 1ページあたりの件数を管理
	const [itemsPerPage, setItemsPerPage] = useState<number>(10);

	// 検索語のデバウンス処理
	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchTerm(searchTerm);
		}, 300);
		return () => clearTimeout(timer);
	}, [searchTerm]);

	// 日付フォーマット関数
	const formatDate = useCallback((dateStr: string) => {
		return new Date(dateStr).toLocaleString();
	}, []);

	// フィルタリングとソート
	const filteredAndSortedAnswers = useMemo(() => {
		return [...answers]
			.filter((answer) => {
				if (!debouncedSearchTerm) return true;
				const searchLower = debouncedSearchTerm.toLowerCase();
				return (
					answer.title.toLowerCase().includes(searchLower) ||
					answer.question_text.toLowerCase().includes(searchLower) ||
					answer.user_selected_choice.toLowerCase().includes(searchLower) ||
					answer.correct_choice.toLowerCase().includes(searchLower) ||
					answer.related_files.some((file) =>
						file.toLowerCase().includes(searchLower),
					) ||
					formatDate(answer.updated_at).toLowerCase().includes(searchLower)
				);
			})
			.sort((a, b) => {
				const direction = sortConfig.direction === "asc" ? 1 : -1;
				const aField = a[sortConfig.field];
				const bField = b[sortConfig.field];

				if (typeof aField === "string" && typeof bField === "string") {
					return direction * aField.localeCompare(bField);
				}

				if (typeof aField === "boolean" && typeof bField === "boolean") {
					return direction * (aField === bField ? 0 : aField ? 1 : -1);
				}

				if (
					sortConfig.field === "updated_at" ||
					sortConfig.field === "created_at"
				) {
					return (
						direction *
						(new Date(aField as string).getTime() -
							new Date(bField as string).getTime())
					);
				}

				return 0;
			});
	}, [answers, sortConfig, debouncedSearchTerm, formatDate]);

	// 選択ハンドラ
	const handleSelect = useCallback((id: number) => {
		setSelectedAnswerIds((prev) => {
			if (prev.includes(id)) {
				return prev.filter((selectedId) => selectedId !== id);
			}
			return [...prev, id];
		});
	}, []);

	// 全選択 / 全解除
	const handleSelectAll = useCallback(() => {
		if (selectedAnswerIds.length === filteredAndSortedAnswers.length) {
			// 全解除
			setSelectedAnswerIds([]);
		} else {
			// 全選択
			const allIds = filteredAndSortedAnswers.map((a) => a.id);
			setSelectedAnswerIds(allIds);
		}
	}, [selectedAnswerIds.length, filteredAndSortedAnswers]);

	// ソートハンドラ
	const handleSort = useCallback((field: keyof AnswerResponse) => {
		setSortConfig((prevConfig) => ({
			field,
			direction:
				prevConfig.field === field && prevConfig.direction === "asc"
					? "desc"
					: "asc",
		}));
	}, []);

	// ソートアイコン取得関数
	const getSortIcon = (field: keyof AnswerResponse) => {
		if (sortConfig.field !== field) return "↕️";
		return sortConfig.direction === "asc" ? "↑" : "↓";
	};

	// モーダルを開くハンドラ
	const handleOpenModal = useCallback((answer: AnswerResponse) => {
		setSelectedAnswer(answer);
		setOpenModal(true);
	}, []);

	// ナビゲーションハンドラ
	const handleNavigate = useCallback(() => {
		if (selectedAnswerIds.length === 0) {
			alert("アイテムを選択してください。");
			return;
		}

		// 追加: ローカルストレージから特定のキーを削除
		for (const key of STORAGE_KEYS_TO_CLEAR) {
			localStorage.removeItem(key);
		}

		// 選択された解答を取得
		const selectedAnswers = answers.filter((answer) =>
			selectedAnswerIds.includes(answer.id),
		);

		// 選択された解答をローカルストレージに保存
		localStorage.setItem("selectedAnswers", JSON.stringify(selectedAnswers));

		// ページ遷移
		router.push("/ai-exercise/select-answers/answers");
	}, [selectedAnswerIds, answers, router]);

	// 削除ボタンクリック時のハンドラ
	const handleDelete = useCallback(async () => {
		if (selectedAnswerIds.length === 0) {
			alert("削除する回答を選択してください。");
			return;
		}

		try {
			const result = await deleteAnswers(selectedAnswerIds);
			if (result.deleted_ids.length > 0) {
				console.log(`削除に成功した回答ID: ${result.deleted_ids.join(", ")}`);
			}
			if (result.not_found_ids.length > 0) {
				console.log(
					`見つからなかった回答ID: ${result.not_found_ids.join(", ")}`,
				);
			}
			if (result.unauthorized_ids.length > 0) {
				console.log(
					`削除権限がなかった回答ID: ${result.unauthorized_ids.join(", ")}`,
				);
			}
			// 削除が完了したら一覧を再取得
			refetch(currentPage, itemsPerPage);
			// 削除後は選択をリセット
			setSelectedAnswerIds([]);
		} catch (err) {
			console.error(err);
		}
	}, [selectedAnswerIds, deleteAnswers, refetch, currentPage, itemsPerPage]);

	// コンテンツを省略する関数
	const truncateContent = (str: string, maxLength = 100): string => {
		return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str;
	};

	// 選択肢IDをフォーマットする関数
	const formatChoiceId = (choiceId: string): string => {
		// choice_a -> A, choice_b -> B などに変換
		const match = choiceId.match(/choice_([a-d])/i);
		if (match) {
			return match[1].toUpperCase();
		}
		return choiceId;
	};

	// 全選択状態かどうかの判定
	const isAllSelected =
		filteredAndSortedAnswers.length > 0 &&
		selectedAnswerIds.length === filteredAndSortedAnswers.length;

	// ▼ ページ切り替え
	const handlePageChange = useCallback(
		(newPage: number) => {
			// 新しいページ番号が有効な数値であることを確認
			if (Number.isNaN(newPage)) {
				console.warn("無効なページ番号です。");
				return;
			}

			if (newPage < 1 || (totalPages && newPage > totalPages)) {
				console.warn("ページ番号が範囲外です。");
				return;
			}
			refetch(newPage, itemsPerPage);
		},
		[totalPages, itemsPerPage, refetch],
	);

	// ▼ 1ページあたりの件数を変更
	const handleItemsPerPageChange = useCallback(
		(newItemsPerPage: number) => {
			if (Number.isNaN(newItemsPerPage) || newItemsPerPage <= 0) {
				console.warn("無効な件数です。");
				return;
			}
			setItemsPerPage(newItemsPerPage);
			// 件数を変更したら1ページ目から再取得
			refetch(1, newItemsPerPage);
		},
		[refetch],
	);

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						解答リスト
					</Typography>
				</CardHeader>

				<CardBody className="flex flex-col gap-4">
					{/* 取得エラー表示 */}
					{error && (
						<Alert
							variant="gradient"
							color="red"
							onClose={() => {
								// エラーをクリアするロジックを追加可能
								// 例: setError("")
							}}
						>
							{error}
						</Alert>
					)}

					{/* 削除エラー表示 */}
					{deleteError && (
						<Alert
							variant="gradient"
							color="red"
							onClose={() => {
								// フックのエラーをクリアするロジックを追加可能
								// 例: setDeleteError("")
							}}
						>
							{deleteError}
						</Alert>
					)}

					<div className="p-4 flex flex-row items-center gap-4">
						<div className="flex-grow md:flex-grow-0 md:w-72">
							<Input
								type="search"
								label="検索"
								value={searchTerm}
								onChange={(e) => setSearchTerm(e.target.value)}
								className="w-full"
							/>
						</div>

						{/* 右上に並べるボタン: 再チャレンジ & 削除 */}
						<div className="ml-auto flex flex-row gap-2">
							<Button
								onClick={handleNavigate}
								disabled={selectedAnswerIds.length === 0}
							>
								問題に再チャレンジ
							</Button>
							<PopupDialog
								buttonTitle="選択項目を削除"
								title="選択項目を削除しますか？"
								actionProps={{ onClick: handleDelete }}
								triggerButtonProps={{
									disabled:
										selectedAnswerIds.length === 0 || loading || deleting,
								}}
							/>
						</div>
					</div>

					{loading ? (
						<div
							className="flex justify-center items-center p-8"
							data-testid="loading-spinner"
						>
							<Spinner className="h-8 w-8" />
						</div>
					) : !answers.length ? (
						<Alert variant="gradient">解答が見つかりません</Alert>
					) : (
						<>
							{/* AnswersTableコンポーネントを使用 */}
							<AnswersTable
								answers={filteredAndSortedAnswers}
								selectedAnswerIds={selectedAnswerIds}
								handleSelect={handleSelect}
								handleSelectAll={handleSelectAll}
								isAllSelected={isAllSelected}
								handleSort={handleSort}
								getSortIcon={getSortIcon}
								truncateContent={truncateContent}
								handleOpenModal={handleOpenModal}
							/>

							{/* ▼ ページネーション UI */}
							<div className="mt-4 flex flex-wrap items-center justify-between gap-4">
								{/* 1ページあたりの件数変更 */}
								<div className="flex items-center space-x-2">
									<Typography variant="small" color="blue-gray">
										件数:
									</Typography>
									<select
										className="border border-blue-gray-200 rounded p-1"
										value={itemsPerPage}
										onChange={(e) =>
											handleItemsPerPageChange(Number(e.target.value))
										}
									>
										<option value={5}>5</option>
										<option value={10}>10</option>
										<option value={25}>25</option>
										<option value={50}>50</option>
										<option value={100}>100</option>
									</select>
									<Typography variant="small" color="blue-gray">
										件/ページ
									</Typography>
								</div>

								{/* 前後ページ送り */}
								<div className="flex items-center justify-center space-x-4">
									<Button
										color="blue"
										variant="outlined"
										onClick={() => handlePageChange(currentPage - 1)}
										disabled={currentPage <= 1}
									>
										前へ
									</Button>
									<Typography variant="small" color="blue-gray">
										{currentPage} / {totalPages} ページ
									</Typography>
									<Button
										color="blue"
										variant="outlined"
										onClick={() => handlePageChange(currentPage + 1)}
										disabled={totalPages === 0 || currentPage >= totalPages}
									>
										次へ
									</Button>
									<Typography
										variant="small"
										color="blue-gray"
										className="ml-4"
									>
										全 {totalCount} 件
									</Typography>
								</div>
							</div>
						</>
					)}
				</CardBody>
			</Card>

			{/* モーダル */}
			<Dialog open={openModal} handler={() => setOpenModal(false)} size="lg">
				<DialogHeader>問題・解答の詳細</DialogHeader>
				<DialogBody divider className="h-96 overflow-auto">
					{selectedAnswer && (
						<div className="space-y-4">
							{/* 質問文 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									質問文
								</Typography>
								<Typography className="whitespace-pre-wrap text-sm">
									{selectedAnswer.question_text}
								</Typography>
							</div>

							{/* 選択肢 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									選択肢
								</Typography>
								<Typography className="text-sm">
									A: {selectedAnswer.choice_a} <br />
									B: {selectedAnswer.choice_b} <br />
									C: {selectedAnswer.choice_c} <br />
									D: {selectedAnswer.choice_d}
								</Typography>
							</div>

							{/* ユーザーの解答 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									ユーザーの解答
								</Typography>
								<Typography className="text-sm">
									{formatChoiceId(selectedAnswer.user_selected_choice)}
								</Typography>
							</div>

							{/* 正解 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									正解
								</Typography>
								<Typography className="text-sm">
									{formatChoiceId(selectedAnswer.correct_choice)}
								</Typography>
							</div>

							{/* 正誤 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									正誤
								</Typography>
								<Typography
									className={`text-sm ${
										selectedAnswer.is_correct
											? "text-green-600"
											: "text-red-600"
									}`}
								>
									{selectedAnswer.is_correct ? "正解" : "不正解"}
								</Typography>
							</div>
							{/* 解説 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									解説
								</Typography>
								<Typography className="whitespace-pre-wrap text-sm">
									{selectedAnswer.explanation}
								</Typography>
							</div>

							{/* 関連ファイル */}
							{selectedAnswer.related_files.length > 0 && (
								<div>
									<Typography variant="h6" className="font-semibold">
										関連ファイル
									</Typography>
									<ul className="list-disc list-inside">
										{selectedAnswer.related_files.map((file) => (
											<li key={file}>
												{file.startsWith("http://") ||
												file.startsWith("https://") ? (
													<a
														href={file}
														target="_blank"
														rel="noopener noreferrer"
														className="text-blue-500 underline"
													>
														{file}
													</a>
												) : (
													<span>{file}</span>
												)}
											</li>
										))}
									</ul>
								</div>
							)}

							{/* 作成日時と更新日時 */}
							<div>
								<Typography variant="h6" className="font-semibold">
									作成日時
								</Typography>
								<Typography className="text-sm">
									{formatDate(selectedAnswer.created_at)}
								</Typography>
							</div>
							<div>
								<Typography variant="h6" className="font-semibold">
									更新日時
								</Typography>
								<Typography className="text-sm">
									{formatDate(selectedAnswer.updated_at)}
								</Typography>
							</div>
						</div>
					)}
				</DialogBody>
			</Dialog>
		</div>
	);
}
