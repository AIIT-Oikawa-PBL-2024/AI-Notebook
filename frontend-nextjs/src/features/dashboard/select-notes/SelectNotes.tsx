"use client";

import { useNoteDelete } from "@/features/dashboard/select-notes/useNoteDelete";
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
const BACKEND_API_URL_NOTES = `${BACKEND_HOST}/notes`;

interface Note {
	id: number;
	title: string;
	content: string;
	user_id: string;
	updated_at: string;
}

type SortField = "updated_at" | "content" | "title";
type SortDirection = "asc" | "desc";

export default function SelectNotesComponent() {
	const router = useRouter();
	const [notes, setNotes] = useState<Note[]>([]);
	const [selectedNoteId, setSelectedNoteId] = useState<number | null>(null);
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
		field: "updated_at",
		direction: "desc",
	});

	const { user } = useAuth();
	const authFetch = useAuthFetch();

	const fetchNotes = useCallback(async () => {
		if (!user) {
			setError("認証が必要です");
			setLoading(false);
			return;
		}

		setLoading(true);
		setError("");

		try {
			const response = await authFetch(
				`${BACKEND_API_URL_NOTES}/${user.uid}/notes`,
			);

			if (!response.ok) {
				throw new Error("ノートの取得に失敗しました");
			}

			const data = await response.json();
			setNotes(data);
		} catch (err) {
			setError(err instanceof Error ? err.message : "エラーが発生しました");
		} finally {
			setLoading(false);
		}
	}, [user, authFetch]);

	const truncateContent = (str: string): string => {
		return str.length > 50 ? `${str.substring(0, 50)}...` : str;
	};

	useEffect(() => {
		fetchNotes();
	}, [fetchNotes]);

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
		setSelectedNoteId(id);
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

	const filteredAndSortedNotes = useMemo(() => {
		return [...notes]
			.filter((note) => {
				if (!debouncedSearchTerm) return true;
				const searchLower = debouncedSearchTerm.toLowerCase();
				return (
					note.title.toLowerCase().includes(searchLower) ||
					note.content.toLowerCase().includes(searchLower) ||
					formatDate(note.updated_at).toLowerCase().includes(searchLower)
				);
			})
			.sort((a, b) => {
				const direction = sortConfig.direction === "asc" ? 1 : -1;

				switch (sortConfig.field) {
					case "title":
						return direction * a.title.localeCompare(b.title);
					case "updated_at":
						return (
							direction *
							(new Date(a.updated_at).getTime() -
								new Date(b.updated_at).getTime())
						);
					case "content":
						return direction * a.content.localeCompare(b.content);
					default:
						return 0;
				}
			});
	}, [notes, sortConfig, debouncedSearchTerm, formatDate]);

	const getSortIcon = (field: SortField) => {
		if (sortConfig.field !== field) return "↕️";
		return sortConfig.direction === "asc" ? "↑" : "↓";
	};

	const handleNavigate = useCallback(() => {
		if (!selectedNoteId) {
			alert("ノートを選択してください。");
			return;
		}

		const selectedNote = notes.find((note) => note.id === selectedNoteId);

		if (!selectedNote) {
			return;
		}

		router.push(`/notebook/${selectedNote.id}`);
	}, [selectedNoteId, notes, router]);

	const { deleteNote, isDeleting } = useNoteDelete({
		onSuccess: () => {
			setSelectedNoteId(null);
			fetchNotes();
		},
		onError: (errorMessage) => {
			setError(errorMessage);
		},
	});

	const handleDelete = async () => {
		if (!selectedNoteId) {
			alert("ノートを選択してください。");
			return;
		}

		if (window.confirm("選択したノートを削除してもよろしいですか？")) {
			await deleteNote(selectedNoteId);
		}
	};

	return (
		<div className="container mx-auto p-4">
			<Card>
				<CardHeader className="mb-4 grid h-28 place-items-center border-b border-gray-200">
					<Typography variant="h3" className="text-gray-900">
						ノートリスト
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
								selectedNoteId
									? "bg-gray-800 hover:bg-gray-600"
									: "bg-gray-400 cursor-not-allowed"
							}`}
							onClick={handleNavigate}
							disabled={!selectedNoteId}
						>
							選択したノートを開く
						</button>
						<button
							type="button"
							className={`px-4 py-2 text-white rounded whitespace-nowrap ${
								selectedNoteId && !isDeleting
									? "bg-blue-gray-800 hover:bg-blue-gray-600"
									: "bg-gray-400 cursor-not-allowed"
							}`}
							onClick={handleDelete}
							disabled={!selectedNoteId || isDeleting}
						>
							{isDeleting ? "削除中..." : "選択したノートを削除"}
						</button>
					</div>

					{loading ? (
						<div className="flex justify-center items-center p-8">
							<Spinner className="h-8 w-8" />
						</div>
					) : !notes.length ? (
						<Alert variant="gradient">ノートが見つかりません</Alert>
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
											onClick={() => handleSort("content")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												内容
											</Typography>
											<span>{getSortIcon("content")}</span>
										</button>
									</th>
									<th className="border-b p-4">
										<button
											type="button"
											onClick={() => handleSort("updated_at")}
											className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
										>
											<Typography
												variant="small"
												className="font-normal leading-none"
											>
												更新日時
											</Typography>
											<span>{getSortIcon("updated_at")}</span>
										</button>
									</th>
								</tr>
							</thead>
							<tbody>
								{filteredAndSortedNotes.map((note) => (
									<tr key={note.id}>
										<td className="p-4">
											<Radio
												name="note-select"
												checked={selectedNoteId === note.id}
												onChange={() => handleSelect(note.id)}
											/>
										</td>
										<td className="p-4">
											<Typography
												variant="small"
												className="font-normal break-words text-xs"
											>
												{note.title}
											</Typography>
										</td>
										<td className="p-4">
											<button
												type="button"
												className="w-full text-left cursor-pointer hover:bg-gray-50"
												onClick={() => handleOpenModal(note.content)}
											>
												<Typography
													variant="small"
													className="font-normal max-w-xs whitespace-pre-wrap text-xs"
												>
													{truncateContent(note.content)}
												</Typography>
											</button>
										</td>
										<td className="p-4">
											<Typography
												variant="small"
												className="font-normal text-xs"
											>
												{formatDate(note.updated_at)}
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
				<DialogHeader>ノートの内容</DialogHeader>
				<DialogBody divider className="h-96 overflow-auto">
					<Typography className="whitespace-pre-wrap">
						{selectedContent}
					</Typography>
				</DialogBody>
			</Dialog>
		</div>
	);
}
