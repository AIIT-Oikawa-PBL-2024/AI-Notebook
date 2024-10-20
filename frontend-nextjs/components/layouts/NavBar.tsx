"use client";
import {
	Card,
	Typography,
	List,
	ListItem,
	ListItemPrefix,
} from "@material-tailwind/react";
import {
	HomeIcon,
	FolderIcon,
	ComputerDesktopIcon,
	PencilSquareIcon,
	PencilIcon,
} from "@heroicons/react/24/solid";

export default function NavBar() {
	return (
		<Card className="h-[calc(100vh-2rem)] w-full max-w-[20rem] p-4 shadow-xl shadow-blue-gray-900/5">
			<div className="mb-2 p-4">
				<Typography variant="h5" color="blue-gray">
					AIノートブック
				</Typography>
			</div>
			<List>
				<ListItem>
					<ListItemPrefix>
						<HomeIcon className="h-5 w-5" />
					</ListItemPrefix>
					ホーム
				</ListItem>
				<ListItem>
					<ListItemPrefix>
						<FolderIcon className="h-5 w-5" />
					</ListItemPrefix>
					ファイル選択
				</ListItem>
				<ListItem>
					<ListItemPrefix>
						<ComputerDesktopIcon className="h-5 w-5" />
					</ListItemPrefix>
					AI出力
				</ListItem>
				<ListItem>
					<ListItemPrefix>
						<PencilSquareIcon className="h-5 w-5" />
					</ListItemPrefix>
					AI練習問題
				</ListItem>
				<ListItem>
					<ListItemPrefix>
						<PencilIcon className="h-5 w-5" />
					</ListItemPrefix>
					ノート
				</ListItem>
			</List>
		</Card>
	);
}
