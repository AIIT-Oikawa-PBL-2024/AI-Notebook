import NavBar from "@/components/layouts/NavBar";
import { ErrorBoundary } from "react-error-boundary";
import DashboardError from "./error";

type LayoutProps = {
	children: React.ReactNode;
};

export default function Layout({ children }: LayoutProps) {
	return (
		<div className="flex">
			<NavBar />
			<ErrorBoundary fallback={<DashboardError />}>
				<main className="flex-1">{children}</main>
			</ErrorBoundary>
		</div>
	);
}
