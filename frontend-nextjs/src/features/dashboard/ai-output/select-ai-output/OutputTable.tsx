"use client";

import { Radio, Typography } from "@material-tailwind/react";

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

interface OutputTableProps {
	outputs: Output[];
	selectedOutputId: number | null;
	handleSelect: (id: number) => void;
	getSortIcon: (field: SortField) => string;
	handleSort: (field: SortField) => void;
	handleOpenModal: (content: string) => void;
	formatStyle: (style: string | null) => string;
	formatDate: (dateStr: string) => string;
	truncateResponse: (str: string) => string;
}

const OutputTable: React.FC<OutputTableProps> = ({
	outputs,
	selectedOutputId,
	handleSelect,
	getSortIcon,
	handleSort,
	handleOpenModal,
	formatStyle,
	formatDate,
	truncateResponse,
}) => {
	return (
		<table className="w-full table-auto text-left">
			<thead className="hidden md:table-header-group">
				<tr>
					<th className="border-b p-4">選択</th>
					<th className="border-b p-4">
						<button
							type="button"
							onClick={() => handleSort("title")}
							className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
						>
							<Typography variant="small" className="font-normal leading-none">
								タイトル
							</Typography>
							<span>{getSortIcon("title")}</span>
						</button>
					</th>
					<th className="border-b p-4">
						<button
							type="button"
							onClick={() => handleSort("files")}
							className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
						>
							<Typography variant="small" className="font-normal leading-none">
								関連ファイル
							</Typography>
							<span>{getSortIcon("files")}</span>
						</button>
					</th>
					<th className="border-b p-4">
						<button
							type="button"
							onClick={() => handleSort("style")}
							className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
						>
							<Typography variant="small" className="font-normal leading-none">
								スタイル
							</Typography>
							<span>{getSortIcon("style")}</span>
						</button>
					</th>
					<th className="border-b p-4">
						<button
							type="button"
							onClick={() => handleSort("output")}
							className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
						>
							<Typography variant="small" className="font-normal leading-none">
								内容
							</Typography>
							<span>{getSortIcon("output")}</span>
						</button>
					</th>
					<th className="border-b p-4">
						<button
							type="button"
							onClick={() => handleSort("created_at")}
							className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded"
						>
							<Typography variant="small" className="font-normal leading-none">
								作成日時
							</Typography>
							<span>{getSortIcon("created_at")}</span>
						</button>
					</th>
				</tr>
			</thead>
			<tbody>
				{outputs.map((output) => (
					<tr key={output.id} className="md:table-row block md:static">
						{/* 選択 */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								選択:
							</span>
							<Radio
								name="output-select"
								checked={selectedOutputId === output.id}
								onChange={() => handleSelect(output.id)}
							/>
						</td>
						{/* タイトル */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								タイトル:
							</span>
							<Typography
								variant="small"
								className="font-normal break-words text-xs"
							>
								{output.title}
							</Typography>
						</td>
						{/* 関連ファイル */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								関連ファイル:
							</span>
							<Typography
								variant="small"
								className="font-normal break-words text-xs"
							>
								{output.files.map((file) => file.file_name).join(", ")}
							</Typography>
						</td>
						{/* スタイル */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								スタイル:
							</span>
							<Typography variant="small" className="font-normal text-xs">
								{formatStyle(output.style)}
							</Typography>
						</td>
						{/* 内容 */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								内容:
							</span>
							<button
								type="button"
								className="w-full text-left cursor-pointer hover:bg-gray-50"
								onClick={() => handleOpenModal(output.output)}
							>
								<Typography
									variant="small"
									className="font-normal max-w-full whitespace-pre-wrap text-xs break-words"
								>
									{truncateResponse(output.output)}
								</Typography>
							</button>
						</td>
						{/* 作成日時 */}
						<td className="p-4 border-b md:border-none block md:table-cell">
							<span className="inline-block md:hidden font-semibold mr-2">
								作成日時:
							</span>
							<Typography variant="small" className="font-normal text-xs">
								{formatDate(output.created_at)}
							</Typography>
						</td>
					</tr>
				))}
			</tbody>
		</table>
	);
};

export default OutputTable;
