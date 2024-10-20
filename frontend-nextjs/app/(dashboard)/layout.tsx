import NavBar from "@/components/layouts/NavBar";

export default function Layout({ children }: { children: React.ReactNode }) {
	return (
		<div className="flex">
			<NavBar />
			<main className="flex-1">{children}</main>
		</div>
	);
}
