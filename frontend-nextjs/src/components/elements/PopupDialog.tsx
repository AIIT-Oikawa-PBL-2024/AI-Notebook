import { Button, type ButtonProps } from "@material-tailwind/react";
import type React from "react";
import { forwardRef } from "react";
import {
	AlertDialog,
	AlertDialogAction,
	AlertDialogCancel,
	AlertDialogContent,
	AlertDialogDescription,
	AlertDialogFooter,
	AlertDialogHeader,
	AlertDialogTitle,
	AlertDialogTrigger,
} from "../ui/alert-dialog";

type Props = {
	buttonTitle: string;
	title: string;
	desc?: string;
	triggerButtonProps?: Omit<ButtonProps, "children">;
	actionProps?: React.ButtonHTMLAttributes<HTMLButtonElement>;
};

export const PopupDialog = forwardRef<HTMLButtonElement, Props>(
	({ buttonTitle, title, desc, triggerButtonProps, actionProps }, ref) => {
		return (
			<AlertDialog>
				<AlertDialogTrigger asChild>
					<Button {...triggerButtonProps} ref={ref}>
						{buttonTitle}
					</Button>
				</AlertDialogTrigger>
				<AlertDialogContent>
					<AlertDialogHeader>
						<AlertDialogTitle>{title}</AlertDialogTitle>
						{desc && <AlertDialogDescription>{desc}</AlertDialogDescription>}
					</AlertDialogHeader>
					<AlertDialogFooter>
						<AlertDialogCancel>キャンセル</AlertDialogCancel>
						<AlertDialogAction {...actionProps}>実行</AlertDialogAction>
					</AlertDialogFooter>
				</AlertDialogContent>
			</AlertDialog>
		);
	},
);

PopupDialog.displayName = "PopupDialog";
