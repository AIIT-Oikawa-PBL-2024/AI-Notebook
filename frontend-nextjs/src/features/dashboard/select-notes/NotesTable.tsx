"use client";

import { Radio, Typography } from "@material-tailwind/react";
import type React from "react";

interface Note {
	id: number;
	title: string;
	content: string;
	user_id: string;
	updated_at: string;
}

type SortField = "updated_at" | "content" | "title";
type SortDirection = "asc" | "desc";

interface NotesTableProps {
	notes: Note[];
	selectedNoteId: number | null;
	handleSelect: (id: number) => void;
	handleOpenModal: (content: string) => void;
	getSortIcon: (field: SortField) => string;
	handleSort: (field: SortField) => void;
	formatDate: (dateStr: string) => string;
	truncateContent: (str: string) => string;
}

const NotesTable: React.FC<NotesTableProps> = ({
	notes,
	selectedNoteId,
	handleSelect,
	handleOpenModal,
	getSortIcon,
	handleSort,
	formatDate,
	truncateContent,
}) => {
	return (
		<div className="overflow-x-auto">
			<table className="w-full table-fixed text-left">
				<thead>
					<tr>
						<th className="border-b p-4 w-1/12">選択</th>
						<th className="border-b p-4 w-3/12">
							<button
								type="button"
								onClick={() => handleSort("title")}
								className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded w-full text-left"
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
						<th className="border-b p-4 w-5/12">
							<button
								type="button"
								onClick={() => handleSort("content")}
								className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded w-full text-left"
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
						<th className="border-b p-4 w-3/12">
							<button
								type="button"
								onClick={() => handleSort("updated_at")}
								className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded w-full text-left"
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
					{notes.map((note) => (
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
									className="font-normal break-words text-xs whitespace-normal"
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
										className="font-normal max-w-full whitespace-normal break-words text-xs"
									>
										{truncateContent(note.content)}
									</Typography>
								</button>
							</td>
							<td className="p-4">
								<Typography
									variant="small"
									className="font-normal text-xs whitespace-normal"
								>
									{formatDate(note.updated_at)}
								</Typography>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
};

export default NotesTable;
