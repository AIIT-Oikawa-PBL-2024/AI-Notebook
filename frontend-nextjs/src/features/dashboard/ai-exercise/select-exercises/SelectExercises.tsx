"use client";

import { useExerciseDelete } from "@/features/dashboard/ai-exercise/select-exercises/useExerciseDelete";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import {
	Alert,
	Card,
	CardBody,
	CardHeader,
	Dialog,
	DialogBody,
	DialogHeader,
	Input,
	Radio,
	Spinner,
	Typography,
} from "@material-tailwind/react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

const BACKEND_HOST = process.env.NEXT_PUBLIC_BACKEND_HOST;
const BACKEND_API_URL_GET_EXERCISES = `${BACKEND_HOST}/exercises/list`;

interface File {
	id: string;
	file_name: string;
	file_size: string;
	created_at: string;
	user_id: string;
}

interface Exercise {
	id: number;
	title: string;
	response: string;
	exercise_type: string;
	user_id: string;
	created_at: string;
	files: File[];
}

type SortField =
	| "exercise_type"
	| "created_at"
	| "response"
	| "files"
	| "title";
type SortDirection = "asc" | "desc";

export default function ExerciseSelectComponent() {
	const router = useRouter();
	const [exercises, setExercises] = useState<Exercise[]>([]);
	const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(
		null,
	);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");
	const [openModal, setOpenModal] = useState(false);
	const [selectedContent, setSelectedContent] = useState("");
	const [searchTerm, setSearchTerm] = useState("");
	const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
	const [sortConfig, setSortConfig] = useState<{
		field: SortField;
		direction: SortDirection;
	}>({
		field: "created_at",
		direction: "desc",
	});

	const { user } = useAuth();
	const authFetch = useAuthFetch();

	const fetchExercises = useCallback(async () => {
		if (!user) {
			setError("認証が必要です");
			setLoading(false);
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(BACKEND_API_URL_GET_EXERCISES);

			if (!response.ok) {
				throw new Error("練習問題の取得に失敗しました");
			}

			const data = await response.json();
			setExercises(
				data.map((exercise: Exercise) => ({
					...exercise,
					response: tryParseJSON(exercise.response),
				})),
			);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	}, [user, authFetch]);

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

	const truncateResponse = (str: string): string => {
		return str.length > 50 ? `${str.substring(0, 50)}...` : str;
	};

	useEffect(() => {
		fetchExercises();
	}, [fetchExercises]);

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchTerm(searchTerm);
		}, 300);

		return () => clearTimeout(timer);
	}, [searchTerm]);

	const formatDate = useCallback((dateStr: string) => {
		return new Date(dateStr).toLocaleString();
	}, []);

	const handleSelect = useCallback((id: number) => {
		setSelectedExerciseId(id);
	}, []);

	const handleOpenModal = (content: string) => {
		setSelectedContent(content);
		setOpenModal(true);
	};

	const handleSort = (field: SortField) => {
		setSortConfig((prevConfig) => ({
			field,
			direction:
				prevConfig.field === field && prevConfig.direction === "asc"
					? "desc"
					: "asc",
		}));
	};

	const filteredAndSortedExercises = useMemo(() => {
		return [...exercises]
			.filter((exercise) => {
				if (!debouncedSearchTerm) return true;
				const searchLower = debouncedSearchTerm.toLowerCase();
				return (
					exercise.title.toLowerCase().includes(searchLower) ||
					exercise.exercise_type.toLowerCase().includes(searchLower) ||
					exercise.response.toLowerCase().includes(searchLower) ||
					exercise.files.some((file) =>
						file.file_name.toLowerCase().includes(searchLower),
					) ||
					formatDate(exercise.created_at).toLowerCase().includes(searchLower)
				);
			})
			.sort((a, b) => {
				const direction = sortConfig.direction === "asc" ? 1 : -1;

				switch (sortConfig.field) {
					case "title":
						return direction * a.title.localeCompare(b.title);
					case "exercise_type":
						return direction * a.exercise_type.localeCompare(b.exercise_type);
					case "created_at":
						return (
							direction *
							(new Date(a.created_at).getTime() -
								new Date(b.created_at).getTime())
						);
					case "response":
						return direction * a.response.localeCompare(b.response);
					case "files": {
						const aFiles = a.files.map((f) => f.file_name).join(", ");
						const bFiles = b.files.map((f) => f.file_name).join(", ");
						return direction * aFiles.localeCompare(bFiles);
					}
					default:
						return 0;
				}
			});
	}, [exercises, sortConfig, debouncedSearchTerm, formatDate]);

	const getExerciseTypeLabel = (type: string) => {
		switch (type) {
			case "multiple_choice":
				return "選択問題";
			case "stream":
				return "総合問題";
			case "essay_question":
				return "記述問題";
			default:
				return type;
		}
	};

	const getSortIcon = (field: SortField) => {
		if (sortConfig.field !== field) return "↕️";
		return sortConfig.direction === "asc" ? "↑" : "↓";
	};

	const handleNavigate = useCallback(() => {
		if (!selectedExerciseId) {
			alert("アイテムを選択してください。");
			return;
		}

		const selectedExercise = exercises.find(
			(exercise) => exercise.id === selectedExerciseId,
		);

		if (!selectedExercise) {
			return;
		}

		switch (selectedExercise.exercise_type) {
			case "multiple_choice":
				router.push(`/ai-exercise/multiple-choice/${selectedExerciseId}`);
				break;
			case "stream":
				router.push(`/ai-exercise/stream/${selectedExerciseId}`);
				break;
			case "essay_question":
				router.push(`/ai-exercise/essay-question/${selectedExerciseId}`);
				break;
			default:
				alert("このタイプのルーティングは未対応です。");
		}
	}, [selectedExerciseId, exercises, router]);

	const { deleteExercise, isDeleting } = useExerciseDelete({
		onSuccess: () => {
			setSelectedExerciseId(null);
			fetchExercises();
		},
		onError: (errorMessage) => {
			setError(errorMessage);
		},
	});

	const handleDelete = async () => {
		if (!selectedExerciseId) {
			alert("アイテムを選択してください。");
			return;
		}

		if (window.confirm("選択した問題を削除してもよろしいですか？")) {
			await deleteExercise(selectedExerciseId);
		}
	};

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						AI練習問題リスト
					</Typography>
				</CardHeader>

				<CardBody className="flex flex-col gap-4">
					{error && (
						<Alert variant="gradient" color="red" onClose={() => setError("")}>
							{error}
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
						<button
							type="button"
							className={`px-4 py-2 text-white rounded whitespace-nowrap ${
								selectedExerciseId
									? "bg-gray-800 hover:bg-gray-600"
									: "bg-gray-400 cursor-not-allowed"
							}`}
							onClick={handleNavigate}
							disabled={!selectedExerciseId}
						>
							選択した問題ページを開く
						</button>
						<button
							type="button"
							className={`px-4 py-2 text-white rounded whitespace-nowrap ${
								selectedExerciseId && !isDeleting
									? "bg-blue-gray-800 hover:bg-blue-gray-600"
									: "bg-gray-400 cursor-not-allowed"
							}`}
							onClick={handleDelete}
							disabled={!selectedExerciseId || isDeleting}
						>
							{isDeleting ? "削除中..." : "選択した問題を削除"}
						</button>
					</div>

					{loading ? (
						<div className="flex justify-center items-center p-8">
							<Spinner className="h-8 w-8" />
						</div>
					) : !exercises.length ? (
						<Alert variant="gradient">練習問題が見つかりません</Alert>
					) : (
						<table className="w-full min-w-max table-auto text-left">
							<thead>
								<tr>
									<th className="border-b p-4">Select</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("title")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												タイトル
											</Typography>
											<span>{getSortIcon("title")}</span>
										</button>
									</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("exercise_type")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												問題の種類
											</Typography>
											<span>{getSortIcon("exercise_type")}</span>
										</button>
									</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("files")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												関連ファイル
											</Typography>
											<span>{getSortIcon("files")}</span>
										</button>
									</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("response")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												内容
											</Typography>
											<span>{getSortIcon("response")}</span>
										</button>
									</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("created_at")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												作成日時
											</Typography>
											<span>{getSortIcon("created_at")}</span>
										</button>
									</th>
								</tr>
							</thead>
							<tbody>
								{filteredAndSortedExercises.map((exercise) => (
									<tr key={exercise.id}>
										<td className="p-4">
											<Radio
												name="exercise-select"
												checked={selectedExerciseId === exercise.id}
												onChange={() => handleSelect(exercise.id)}
											/>
										</td>
										<td className="p-4 max-w-[200px]">
											<Typography
												variant="small"
												className="font-normal break-words text-xs"
											>
												{exercise.title}
											</Typography>
										</td>
										<td className="p-4">
											<Typography
												variant="small"
												className="font-normal break-words text-xs"
											>
												{getExerciseTypeLabel(exercise.exercise_type)}
											</Typography>
										</td>
										<td className="p-4 max-w-[200px]">
											<Typography
												variant="small"
												className="font-normal break-words text-xs"
											>
												{exercise.files
													.map((file) => file.file_name)
													.join(", ")}
											</Typography>
										</td>
										<td className="p-4">
											<button
												type="button"
												className="w-full text-left cursor-pointer hover:bg-gray-50"
												onClick={() => handleOpenModal(exercise.response)}
											>
												<Typography
													variant="small"
													className="font-normal max-w-xs whitespace-pre-wrap text-xs"
												>
													{truncateResponse(exercise.response)}
												</Typography>
											</button>
										</td>
										<td className="p-4">
											<Typography
												variant="small"
												className="font-normal text-xs"
											>
												{formatDate(exercise.created_at)}
											</Typography>
										</td>
									</tr>
								))}
							</tbody>
						</table>
					)}
				</CardBody>
			</Card>

			<Dialog open={openModal} handler={() => setOpenModal(false)} size="lg">
				<DialogHeader>問題の内容</DialogHeader>
				<DialogBody divider className="h-96 overflow-auto">
					<Typography className="whitespace-pre-wrap">
						{selectedContent}
					</Typography>
				</DialogBody>
			</Dialog>
		</div>
	);
}
