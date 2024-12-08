import { Button } from "@material-tailwind/react";
import type { ButtonHTMLAttributes } from "react";

type SecondaryButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
	size?: "sm" | "md" | "lg";
	children: React.ReactNode;
	color?: "blue" | "gray" | "green" | "red" | "yellow";
};

const SecondaryButton = ({
	size = "sm",
	color = "blue",
	children,
	...props
}: SecondaryButtonProps) => {
	return (
		<Button color="blue" variant="outlined" size={size} {...props}>
			{children}
		</Button>
	);
};

export default SecondaryButton;
