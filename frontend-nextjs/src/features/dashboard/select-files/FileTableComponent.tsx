import { Card, Checkbox, Input, Typography } from "@material-tailwind/react";
import type React from "react";
import { useState } from "react";

interface FileData {
	file_name: string;
	file_size: string | number;
	created_at: string;
	select?: boolean;
	id?: string;
	user_id?: string;
}

interface FileTableProps {
	files: FileData[];
	loading: boolean;
	handleSelect: (fileName: string, checked: boolean) => void;
	handleSelectAll: (checked: boolean) => void;
	areAllFilesSelected: boolean;
	formatDate: (dateStr: string) => string;
}

type SortKey = "file_name" | "file_size" | "created_at";
type SortDirection = "asc" | "desc";

const FileTable: React.FC<FileTableProps> = ({
	files,
	loading,
	handleSelect,
	handleSelectAll,
	areAllFilesSelected,
	formatDate,
}) => {
	const [sortKey, setSortKey] = useState<SortKey>("file_name");
	const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
	const [searchQuery, setSearchQuery] = useState("");

	const formatFileSize = (bytes: number): string => {
		if (bytes >= 1024 * 1024) {
			return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
		}
		return `${(bytes / 1024).toFixed(2)} KB`;
	};

	const handleSort = (key: SortKey) => {
		if (sortKey === key) {
			setSortDirection(sortDirection === "asc" ? "desc" : "asc");
		} else {
			setSortKey(key);
			setSortDirection("asc");
		}
	};

	const getFileSizeInBytes = (fileSize: string | number): number => {
		if (typeof fileSize === "number") {
			return fileSize;
		}

		try {
			const parts = fileSize.trim().split(" ");
			if (parts.length !== 2) {
				return Number(fileSize) || 0;
			}

			const value = Number.parseFloat(parts[0]);
			const unit = parts[1].toUpperCase();
			const multipliers = {
				B: 1,
				KB: 1024,
				MB: 1024 * 1024,
				GB: 1024 * 1024 * 1024,
			};

			return value * (multipliers[unit as keyof typeof multipliers] || 1);
		} catch {
			return 0;
		}
	};

	const filterFiles = (files: FileData[]) => {
		if (!searchQuery) return files;

		const query = searchQuery.toLowerCase();
		return files.filter((file) => file.file_name.toLowerCase().includes(query));
	};

	const getSortedFiles = () => {
		return filterFiles([...files]).sort((a, b) => {
			let compareValue: number;

			if (sortKey === "file_size") {
				const aBytes = getFileSizeInBytes(a[sortKey]);
				const bBytes = getFileSizeInBytes(b[sortKey]);
				compareValue = aBytes - bBytes;
			} else if (sortKey === "created_at") {
				compareValue =
					new Date(a[sortKey]).getTime() - new Date(b[sortKey]).getTime();
			} else {
				compareValue = a[sortKey]
					.toString()
					.localeCompare(b[sortKey].toString(), "ja");
			}

			return sortDirection === "asc" ? compareValue : -compareValue;
		});
	};

	const getSortIcon = (key: SortKey) => {
		if (sortKey !== key) return "↕";
		return sortDirection === "asc" ? "↑" : "↓";
	};

	return (
		<Card>
			<div className="p-4">
				<input
					type="text"
					placeholder="ファイル名で検索"
					value={searchQuery}
					onChange={(e) => setSearchQuery(e.target.value)}
					className="w-full max-w-xs px-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-800 focus:border-transparent"
				/>
			</div>
			<table className="w-full min-w-max table-auto text-left">
				<thead>
					<tr>
						<th className="border-b p-4">
							<Checkbox
								checked={areAllFilesSelected}
								onChange={(e) => handleSelectAll(e.target.checked)}
								disabled={loading}
							/>
						</th>
						<th
							className="border-b p-4 cursor-pointer"
							onClick={() => handleSort("file_name")}
							onKeyUp={(e) => e.key === "Enter" && handleSort("file_name")}
						>
							<Typography variant="small" className="font-normal leading-none">
								ファイル名 {getSortIcon("file_name")}
							</Typography>
						</th>
						<th
							className="border-b p-4 cursor-pointer"
							onClick={() => handleSort("file_size")}
							onKeyUp={(e) => e.key === "Enter" && handleSort("file_size")}
						>
							<Typography variant="small" className="font-normal leading-none">
								サイズ {getSortIcon("file_size")}
							</Typography>
						</th>
						<th
							className="border-b p-4 cursor-pointer"
							onClick={() => handleSort("created_at")}
							onKeyUp={(e) => e.key === "Enter" && handleSort("created_at")}
						>
							<Typography variant="small" className="font-normal leading-none">
								作成日時 {getSortIcon("created_at")}
							</Typography>
						</th>
					</tr>
				</thead>
				<tbody>
					{getSortedFiles().map((file) => (
						<tr key={file.file_name}>
							<td className="p-4">
								<Checkbox
									checked={file.select}
									onChange={(e) =>
										handleSelect(file.file_name, e.target.checked)
									}
									disabled={loading}
								/>
							</td>
							<td className="p-4">
								<Typography variant="small">{file.file_name}</Typography>
							</td>
							<td className="p-4">
								<Typography variant="small">
									{formatFileSize(getFileSizeInBytes(file.file_size))}
								</Typography>
							</td>
							<td className="p-4">
								<Typography variant="small">
									{formatDate(file.created_at)}
								</Typography>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</Card>
	);
};

export default FileTable;
