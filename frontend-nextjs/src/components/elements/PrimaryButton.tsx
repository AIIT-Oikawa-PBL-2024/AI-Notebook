import { Button } from "@material-tailwind/react";
import type { ButtonHTMLAttributes } from "react";

type PrimaryButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
	size?: "sm" | "md" | "lg";
	children: React.ReactNode;
	color?: "blue" | "gray" | "green" | "red" | "yellow";
};

const PrimaryButton = ({
	size = "sm",
	color = "blue",
	children,
	...props
}: PrimaryButtonProps) => {
	return (
		<Button color="blue" size={size} {...props}>
			{children}
		</Button>
	);
};

export default PrimaryButton;
