"use client";

import { PopupDialog } from "@/components/elements/PopupDialog";
import NotesTable from "@/features/dashboard/select-notes/NotesTable";
import { useNoteDelete } from "@/features/dashboard/select-notes/useNoteDelete";
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
		if (!selectedNoteId) return;
		await deleteNote(selectedNoteId);
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
						<Button
							onClick={handleNavigate}
							disabled={!selectedNoteId || loading}
						>
							選択したノートを開く
						</Button>
						<PopupDialog
							buttonTitle="選択したノートを削除"
							title="選択したノートを削除しますか？"
							actionProps={{ onClick: handleDelete }}
							triggerButtonProps={{ disabled: !selectedNoteId || isDeleting }}
						/>
					</div>

					{loading ? (
						<div className="flex justify-center items-center p-8">
							<Spinner className="h-8 w-8" />
						</div>
					) : !notes.length ? (
						<Alert variant="gradient">ノートが見つかりません</Alert>
					) : (
						<NotesTable
							notes={filteredAndSortedNotes}
							selectedNoteId={selectedNoteId}
							handleSelect={handleSelect}
							handleOpenModal={handleOpenModal}
							getSortIcon={getSortIcon}
							handleSort={handleSort}
							formatDate={formatDate}
							truncateContent={truncateContent}
						/>
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
