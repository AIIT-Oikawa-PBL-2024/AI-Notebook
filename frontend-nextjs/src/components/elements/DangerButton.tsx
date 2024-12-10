import { Button } from "@material-tailwind/react";
import type { ButtonHTMLAttributes } from "react";

type DangerButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
	size?: "sm" | "md" | "lg";
	children: React.ReactNode;
	color?: "red";
};

const DangerButton = ({
	size = "sm",
	color = "red",
	children,
	...props
}: DangerButtonProps) => {
	return (
		<Button color="red" size={size} {...props}>
			{children}
		</Button>
	);
};

export default DangerButton;
