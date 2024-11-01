"use client";

import { Spinner } from "@material-tailwind/react";

export default function Loading() {
	return (
		<div
			className="flex items-center justify-center min-h-screen"
			aria-label="Loading content"
		>
			<Spinner className="h-8 w-8" />
		</div>
	);
}
