import { Inter, Noto_Sans_JP } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/providers/AuthProvider";
import ClientThemeProvider from "@/providers/ClientThemeProvider";
import type { Metadata } from "next";
import { ErrorBoundary } from "react-error-boundary";
import DashboardError from "./(dashboard)/error";

const notoSansJP = Noto_Sans_JP({
	subsets: ["latin"],
	variable: "--font-noto-sans-jp",
});

const inter = Inter({
	subsets: ["latin"],
	variable: "--font-inter",
});

export const metadata: Metadata = {
	title: "AI-Notebook",
	description: "AI-powered app for creating notes",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="ja">
			<body
				className={`${notoSansJP.variable} ${inter.variable} font-sans antialiased`}
				style={{
					fontFamily: `var(--font-inter), var(--font-noto-sans-jp), Arial, 'Helvetica Neue', sans-serif`,
				}}
			>
				<ClientThemeProvider>
					<ErrorBoundary fallback={<DashboardError />}>
						<AuthProvider>{children}</AuthProvider>
					</ErrorBoundary>
				</ClientThemeProvider>
			</body>
		</html>
	);
}
