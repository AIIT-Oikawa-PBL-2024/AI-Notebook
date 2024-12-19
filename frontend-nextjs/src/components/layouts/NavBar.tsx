"use client";

import { useSignOut } from "@/hooks/useSignOut";
import { useAuth } from "@/providers/AuthProvider";
import {
	BookOpenIcon,
	CloudArrowUpIcon,
	ComputerDesktopIcon,
	DocumentCheckIcon,
	DocumentTextIcon,
	FolderIcon,
	HomeIcon,
	ListBulletIcon,
	PencilIcon,
	PencilSquareIcon,
	QuestionMarkCircleIcon,
} from "@heroicons/react/24/solid";
import {
	Accordion,
	AccordionBody,
	AccordionHeader,
	Button,
	Card,
	List,
	ListItem,
	ListItemPrefix,
	Typography,
} from "@material-tailwind/react";
import Link from "next/link";
import { useState } from "react";

// Define a type for navigation items
type NavItem = {
	name: string;
	href: string;
	icon: React.ComponentType<{ className?: string }>;
};

// Define group icons
const groupIcons: Record<
	string,
	React.ComponentType<{ className?: string }>
> = {
	AI要約: DocumentTextIcon,
	AI練習問題: QuestionMarkCircleIcon,
	ノート: BookOpenIcon,
};

// Define navigation groups
const navigationGroups = [
	{
		name: "AI要約",
		items: [
			{
				name: "AI要約リスト",
				href: "/ai-output/select-ai-output",
				icon: ListBulletIcon,
			},
			{ name: "AI要約", href: "/ai-output/stream", icon: ComputerDesktopIcon },
		],
	},
	{
		name: "AI練習問題",
		items: [
			{
				name: "AI練習問題リスト",
				href: "/ai-exercise/select-exercises",
				icon: ListBulletIcon,
			},
			{
				name: "AI練習問題",
				href: "/ai-exercise/stream",
				icon: PencilSquareIcon,
			},
			{
				name: "選択問題テスト",
				href: "/ai-exercise/multiple-choice",
				icon: DocumentCheckIcon,
			},
			{
				name: "記述問題テスト",
				href: "/ai-exercise/essay-question",
				icon: DocumentCheckIcon,
			},
		],
	},
	{
		name: "ノート",
		items: [
			{ name: "ノートリスト", href: "/select-notes", icon: ListBulletIcon },
			{ name: "ノート作成", href: "/notebook", icon: PencilIcon },
		],
	},
];

export default function NavBar() {
	const { user } = useAuth();
	const { signOutUser, error, isLoading } = useSignOut();
	const [openGroup, setOpenGroup] = useState<string | null>(null);

	if (!user) {
		return null;
	}

	const handleGroupToggle = (groupName: string) => {
		setOpenGroup(openGroup === groupName ? null : groupName);
	};

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
				{/* Direct navigation items */}
				<Link href="/">
					<ListItem>
						<ListItemPrefix>
							<CloudArrowUpIcon className="h-5 w-5" />
						</ListItemPrefix>
						アップロード
					</ListItem>
				</Link>
				<Link href="/select-files">
					<ListItem>
						<ListItemPrefix>
							<FolderIcon className="h-5 w-5" />
						</ListItemPrefix>
						ファイル選択
					</ListItem>
				</Link>

				{/* Grouped navigation items */}
				{navigationGroups.map((group) => (
					<div key={group.name} className="mb-2">
						<Accordion
							open={openGroup === group.name}
							icon={
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									strokeWidth={2}
									stroke="currentColor"
									className={`h-5 w-5 transition-transform ${
										openGroup === group.name ? "rotate-180" : ""
									}`}
								>
									<title>
										{openGroup === group.name ? "Collapse" : "Expand"}
									</title>
									<path
										strokeLinecap="round"
										strokeLinejoin="round"
										d="M19.5 8.25l-7.5 7.5-7.5-7.5"
									/>
								</svg>
							}
						>
							<AccordionHeader
								onClick={() => handleGroupToggle(group.name)}
								className="border-b-0 p-3 flex items-center space-x-2"
								data-testid={`accordion-header-${group.name}`}
							>
								{/* グループアイコン */}
								{groupIcons[group.name] &&
									(() => {
										const IconComponent = groupIcons[group.name];
										return (
											<IconComponent className="h-5 w-5 text-blue-gray-500" />
										);
									})()}
								<Typography
									color="blue-gray"
									className="flex-1 text-left font-normal"
								>
									{group.name}
								</Typography>
							</AccordionHeader>
							<AccordionBody className="py-1">
								<List className="p-0">
									{group.items.map((item) => (
										<Link href={item.href} key={item.href}>
											<ListItem>
												<ListItemPrefix>
													<item.icon className="h-5 w-5" />
												</ListItemPrefix>
												{item.name}
											</ListItem>
										</Link>
									))}
								</List>
							</AccordionBody>
						</Accordion>
					</div>
				))}
			</List>
		</Card>
	);
}
