"use client";

import type { AnswerResponse } from "@/features/dashboard/ai-exercise/select-answers/useFetchAnswers";
import { Checkbox, Typography } from "@material-tailwind/react";

interface AnswersTableProps {
	answers: AnswerResponse[];
	selectedAnswerIds: number[];
	handleSelect: (id: number) => void;
	handleSelectAll: () => void;
	isAllSelected: boolean;
	handleSort: (field: keyof AnswerResponse) => void;
	getSortIcon: (field: keyof AnswerResponse) => string;
	truncateContent: (str: string, maxLength?: number) => string;
	handleOpenModal: (answer: AnswerResponse) => void;
}

export const AnswersTable: React.FC<AnswersTableProps> = ({
	answers,
	selectedAnswerIds,
	handleSelect,
	handleSelectAll,
	isAllSelected,
	handleSort,
	getSortIcon,
	truncateContent,
	handleOpenModal,
}) => {
	return (
		<div className="overflow-hidden">
			<table className="w-full min-w-full table-fixed text-left">
				<thead>
					<tr>
						<th className="border-b p-4 w-12">
							<Checkbox
								checked={isAllSelected}
								onChange={handleSelectAll}
								aria-label="全選択"
							/>
						</th>
						<th className="border-b p-4 w-1/6">
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
						<th className="border-b p-4 w-1/4">
							<button
								type="button"
								onClick={() => handleSort("question_text")}
								className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded w-full text-left"
							>
								<Typography
									variant="small"
									className="font-normal leading-none"
								>
									質問文
								</Typography>
								<span>{getSortIcon("question_text")}</span>
							</button>
						</th>
						<th className="border-b p-4 w-1/4">選択肢</th>
						<th className="border-b p-4 w-1/12">
							<button
								type="button"
								onClick={() => handleSort("is_correct")}
								className="flex items-center gap-1 hover:bg-gray-50 px-2 py-1 rounded w-full text-left"
							>
								<Typography
									variant="small"
									className="font-normal leading-none"
								>
									正誤
								</Typography>
								<span>{getSortIcon("is_correct")}</span>
							</button>
						</th>
						<th className="border-b p-4 w-1/6">
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
					{answers.map((answer) => (
						<tr key={answer.id} className="hover:bg-gray-100">
							<td className="p-4 w-12">
								<Checkbox
									name={`answer-select-${answer.id}`}
									checked={selectedAnswerIds.includes(answer.id)}
									onChange={(e) => {
										e.stopPropagation();
										handleSelect(answer.id);
									}}
									aria-label={`選択 ${answer.title}`}
								/>
							</td>
							<td className="p-4 w-1/6">
								<Typography
									variant="small"
									className="font-normal break-words text-xs whitespace-normal"
								>
									{answer.title}
								</Typography>
							</td>
							<td className="p-4 w-1/4">
								{/* 質問文をクリック可能にする */}
								<button
									type="button"
									onClick={(e) => {
										e.stopPropagation(); // 他のイベントの発火を防ぐ
										handleOpenModal(answer);
									}}
									onKeyDown={(e) => {
										if (e.key === "Enter" || e.key === " ") {
											e.preventDefault();
											handleOpenModal(answer);
										}
									}}
									className="w-full text-left focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
									aria-label={`質問文を開く: ${answer.question_text}`}
								>
									<Typography
										variant="small"
										className="font-normal whitespace-normal text-xs hover:underline"
									>
										{truncateContent(answer.question_text, 100)}
									</Typography>
								</button>
							</td>
							<td className="p-4 w-1/4">
								<Typography
									variant="small"
									className="font-normal break-words text-xs whitespace-normal"
								>
									A: {answer.choice_a} <br />
									B: {answer.choice_b} <br />
									C: {answer.choice_c} <br />
									D: {answer.choice_d}
								</Typography>
							</td>
							<td className="p-4 w-1/12">
								<Typography
									variant="small"
									className={`font-normal text-xs ${
										answer.is_correct ? "text-green-600" : "text-red-600"
									} whitespace-normal`}
								>
									{answer.is_correct ? "正解" : "不正解"}
								</Typography>
							</td>
							<td className="p-4 w-1/6">
								<Typography
									variant="small"
									className="font-normal text-xs whitespace-normal"
								>
									{new Date(answer.updated_at).toLocaleString()}
								</Typography>
							</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
};
