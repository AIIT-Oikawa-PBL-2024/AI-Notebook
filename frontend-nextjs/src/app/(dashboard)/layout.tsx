import NavBar from "@/components/layouts/NavBar";

type LayoutProps = {
	children: React.ReactNode;
};

export default function Layout({ children }: LayoutProps) {
	return (
		<div className="flex">
			<NavBar />
			<main className="flex-1">{children}</main>
		</div>
	);
}
