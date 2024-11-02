"use client";

import { useSignOut } from "@/hooks/useSignOut";
import { useAuth } from "@/providers/AuthProvider";
import {
	ComputerDesktopIcon,
	FolderIcon,
	HomeIcon,
	PencilIcon,
	PencilSquareIcon,
} from "@heroicons/react/24/solid";
import {
	Button,
	Card,
	List,
	ListItem,
	ListItemPrefix,
	Typography,
} from "@material-tailwind/react";
import Link from "next/link";

export default function NavBar() {
	const { user } = useAuth();
	const { signOutUser, error, isLoading } = useSignOut();

	if (!user) {
		return null; // ユーザーが存在しない場合は何も表示しない
	}

	return (
		<Card className="h-[calc(100vh-2rem)] w-full max-w-[20rem] p-4 shadow-xl shadow-blue-gray-900/5 sticky top-4 self-start overflow-y-auto">
			<div className="mb-2 p-4">
				<Typography variant="h5" color="blue-gray">
					<Link href="/">AIノートブック</Link>
				</Typography>
			</div>
			{user && (
				<div className="w-full px-4 py-2 text-gray-600 bg-gray-100 rounded-md">
					<Typography variant="small" className="block w-full text-center">
						ユーザー: {user.displayName || user.email}
					</Typography>
					<Button
						onClick={signOutUser}
						disabled={isLoading}
						className="mt-2 w-full bg-gray-200 text-black hover:bg-gray-300"
					>
						{isLoading ? "サインアウト中..." : "サインアウト"}
					</Button>
					{error && (
						<Typography variant="small" color="red" className="mt-2">
							{error}
						</Typography>
					)}
				</div>
			)}
			<List className="mt-4">
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
				<Link href="/ai-output">
					<ListItem>
						<ListItemPrefix>
							<ComputerDesktopIcon className="h-5 w-5" />
						</ListItemPrefix>
						AI出力
					</ListItem>
				</Link>
				<ListItem>
					<ListItemPrefix>
						<PencilSquareIcon className="h-5 w-5" />
					</ListItemPrefix>
					AI練習問題
				</ListItem>
				<Link href="/notebook">
					<ListItem>
						<ListItemPrefix>
							<PencilIcon className="h-5 w-5" />
						</ListItemPrefix>
						ノート
					</ListItem>
				</Link>
			</List>
		</Card>
	);
}
