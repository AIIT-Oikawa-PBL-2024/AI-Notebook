"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/providers/AuthProvider";

export function withAuth<P extends JSX.IntrinsicAttributes>(
	WrappedComponent: React.ComponentType<P>,
) {
	return (props: P) => {
		const { user } = useAuth();
		const router = useRouter();

		useEffect(() => {
			if (!user) {
				router.push("/signin");
			}
		}, [user, router]);

		if (!user) {
			return null; // または、ローディングインジケータを表示
		}

		return <WrappedComponent {...props} />;
	};
}
