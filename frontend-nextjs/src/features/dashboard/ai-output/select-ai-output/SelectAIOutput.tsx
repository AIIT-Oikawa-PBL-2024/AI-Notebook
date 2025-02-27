"use client";

import { PopupDialog } from "@/components/elements/PopupDialog";
import OutputTable from "@/features/dashboard/ai-output/select-ai-output/OutputTable";
import { useNoteInitialData } from "@/features/dashboard/ai-output/select-ai-output/useNoteInitialData";
import { useOutputDelete } from "@/features/dashboard/ai-output/select-ai-output/useOutputDelete";
import { useAuthFetch } from "@/hooks/useAuthFetch";
import { useAuth } from "@/providers/AuthProvider";
import {
	Alert,
	Button,
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
const BACKEND_API_URL_GET_OUTPUTS = `${BACKEND_HOST}/outputs/list`;

// ファイルに関する型定義
interface File {
	id: string;
	file_name: string;
	file_size: string;
	created_at: string;
	user_id: string;
}

// 出力に関する型定義
interface Output {
	id: number;
	title: string;
	output: string;
	user_id: string;
	created_at: string;
	files: File[];
	style: string; // 新しいプロパティを追加
}

type SortField = "created_at" | "output" | "files" | "title" | "style";
type SortDirection = "asc" | "desc";

export default function OutputSelectComponent() {
	const router = useRouter();
	const [outputs, setOutputs] = useState<Output[]>([]);
	const [selectedOutputId, setSelectedOutputId] = useState<number | null>(null);
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
	const { setInitialData } = useNoteInitialData();

	// 出力データを取得する関数
	const fetchOutputs = useCallback(async () => {
		if (!user) {
			setError("認証が必要です");
			setLoading(false);
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(BACKEND_API_URL_GET_OUTPUTS);

			if (!response.ok) {
				throw new Error("AI要約の取得に失敗しました");
			}

			const data = await response.json();
			setOutputs(
				data.map((output: Output) => ({
					...output,
					response: tryParseJSON(output.output),
				})),
			);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	}, [user, authFetch]);

	// JSON文字列をパースする関数
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

	// レスポンスを切り捨てる関数
	const truncateResponse = (str: string): string => {
		return str.length > 50 ? `${str.substring(0, 50)}...` : str;
	};

	// コンポーネントのマウント時に出力データを取得
	useEffect(() => {
		fetchOutputs();
	}, [fetchOutputs]);

	// 検索語のデバウンス処理
	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedSearchTerm(searchTerm);
		}, 300);

		return () => clearTimeout(timer);
	}, [searchTerm]);

	// 日付をフォーマットする関数
	const formatDate = useCallback((dateStr: string) => {
		return new Date(dateStr).toLocaleString();
	}, []);

	// スタイルを日本語に変換する関数
	const formatStyle = (style: string | null): string => {
		switch (style) {
			case "simple":
				return "シンプル";
			case "casual":
				return "カジュアル";
			default:
				return "";
		}
	};

	// 出力の選択を処理する関数
	const handleSelect = useCallback((id: number) => {
		setSelectedOutputId(id);
	}, []);

	// モーダルを開く関数
	const handleOpenModal = (content: string) => {
		setSelectedContent(content);
		setOpenModal(true);
	};

	// ソートを処理する関数
	const handleSort = (field: SortField) => {
		setSortConfig((prevConfig) => ({
			field,
			direction:
				prevConfig.field === field && prevConfig.direction === "asc"
					? "desc"
					: "asc",
		}));
	};

	// フィルタリングおよびソートされた出力を取得
	const filteredAndSortedOutputs = useMemo(() => {
		const formatStyleLocal = (style: string | null): string => {
			switch (style) {
				case "simple":
					return "シンプル";
				case "casual":
					return "カジュアル";
				default:
					return "";
			}
		};

		return [...outputs]
			.filter((output) => {
				if (!debouncedSearchTerm) return true;
				const searchLower = debouncedSearchTerm.toLowerCase();
				return (
					output.title.toLowerCase().includes(searchLower) ||
					output.output.toLowerCase().includes(searchLower) ||
					output.files.some((file) =>
						file.file_name.toLowerCase().includes(searchLower),
					) ||
					formatDate(output.created_at).toLowerCase().includes(searchLower) ||
					formatStyleLocal(output.style).toLowerCase().includes(searchLower) // スタイルでの検索を修正
				);
			})
			.sort((a, b) => {
				const direction = sortConfig.direction === "asc" ? 1 : -1;

				switch (sortConfig.field) {
					case "title":
						return direction * a.title.localeCompare(b.title);
					case "created_at":
						return (
							direction *
							(new Date(a.created_at).getTime() -
								new Date(b.created_at).getTime())
						);
					case "output":
						return direction * a.output.localeCompare(b.output);
					case "files": {
						const aFiles = a.files.map((f) => f.file_name).join(", ");
						const bFiles = b.files.map((f) => f.file_name).join(", ");
						return direction * aFiles.localeCompare(bFiles);
					}
					case "style": // スタイルでのソートを追加
						return direction * a.style.localeCompare(b.style);
					default:
						return 0;
				}
			});
	}, [outputs, sortConfig, debouncedSearchTerm, formatDate]);

	// ソートアイコンを取得する関数
	const getSortIcon = (field: SortField) => {
		if (sortConfig.field !== field) return "↕️";
		return sortConfig.direction === "asc" ? "↑" : "↓";
	};

	// 選択したAI要約ページに移動する関数
	const handleNavigate = useCallback(() => {
		if (!selectedOutputId) {
			alert("アイテムを選択してください。");
			return;
		}

		const selectedOutput = outputs.find(
			(output) => output.id === selectedOutputId,
		);

		if (!selectedOutput) {
			return;
		}

		router.push(`/ai-output/stream/${selectedOutput.id}`);
	}, [selectedOutputId, outputs, router]);

	// 出力の削除を処理するフック
	const { deleteOutput, isDeleting } = useOutputDelete({
		onSuccess: () => {
			setSelectedOutputId(null);
			fetchOutputs();
		},
		onError: (errorMessage) => {
			setError(errorMessage);
		},
	});

	// 出力を削除する関数
	const handleDelete = async () => {
		if (!selectedOutputId) return;
		await deleteOutput(selectedOutputId);
	};

	// ノートを作成する関数
	const handleCreateNote = useCallback(() => {
		if (!selectedOutputId) {
			alert("アイテムを選択してください。");
			return;
		}

		const selectedOutput = outputs.find(
			(output) => output.id === selectedOutputId,
		);

		if (!selectedOutput) {
			return;
		}

		setInitialData({
			title: selectedOutput.title,
			content: selectedOutput.output,
		});

		router.push("/notebook");
	}, [selectedOutputId, outputs, router, setInitialData]);

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						AI要約リスト
					</Typography>
				</CardHeader>

				<CardBody className="flex flex-col gap-4">
					{error && (
						<Alert variant="gradient" color="red" onClose={() => setError("")}>
							{error}
						</Alert>
					)}

					<div className="p-4 flex flex-col md:flex-row items-center gap-4">
						<div className="flex-grow md:flex-grow-0 md:w-72">
							<Input
								type="search"
								label="検索"
								value={searchTerm}
								onChange={(e) => setSearchTerm(e.target.value)}
								className="w-full"
							/>
						</div>
						<Button onClick={handleNavigate} disabled={!selectedOutputId}>
							選択したAI要約ページを開く
						</Button>
						<PopupDialog
							buttonTitle="AI要約を削除"
							title="選択したAI要約を削除しますか？"
							actionProps={{ onClick: handleDelete }}
							triggerButtonProps={{ disabled: !selectedOutputId || isDeleting }}
						/>
						<Button onClick={handleCreateNote} disabled={!selectedOutputId}>
							ノートを作成
						</Button>
					</div>

					{loading ? (
						<div className="flex justify-center items-center p-8">
							<Spinner className="h-8 w-8" />
						</div>
					) : !outputs.length ? (
						<Alert variant="gradient">AI要約が見つかりません</Alert>
					) : (
						<OutputTable
							outputs={filteredAndSortedOutputs}
							selectedOutputId={selectedOutputId}
							handleSelect={handleSelect}
							getSortIcon={getSortIcon}
							handleSort={handleSort}
							handleOpenModal={handleOpenModal}
							formatStyle={formatStyle}
							formatDate={formatDate}
							truncateResponse={truncateResponse}
						/>
					)}
				</CardBody>
			</Card>

			<Dialog open={openModal} handler={() => setOpenModal(false)} size="lg">
				<DialogHeader>AI要約の内容</DialogHeader>
				<DialogBody divider className="h-96 overflow-auto">
					<Typography className="whitespace-pre-wrap">
						{selectedContent}
					</Typography>
				</DialogBody>
			</Dialog>
		</div>
	);
}
