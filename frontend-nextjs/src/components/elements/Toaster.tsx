import { toast } from "sonner";

type Props = {
	message: string;
	type: "success" | "error" | "info" | "warning";
};

export const Toaster = ({ message, type = "info" }: Props) => {
	if (type === "success")
		return toast.success(message, {
			position: "top-center",
			style: { background: "#d7f7e0", color: "#000000" },
		});
	if (type === "info")
		return toast.info(message, {
			position: "top-center",
			style: { background: "#d9f5ff", color: "#000000" },
		});
	if (type === "warning")
		return toast.warning(message, {
			position: "top-center",
			style: { background: "#f7f7a1", color: "#000000" },
		});
	if (type === "error")
		return toast.error(message, {
			position: "top-center",
			style: { background: "#ffbaba", color: "#000000" },
		});
};
