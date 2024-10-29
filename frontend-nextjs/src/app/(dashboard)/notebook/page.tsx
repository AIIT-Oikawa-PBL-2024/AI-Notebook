"use client";

import { withAuth } from "@/utils/withAuth";
import type { NextPage } from "next";

const NotebookListPage: NextPage = () => {
	return (
		<div>
			<h1>NotebookListPage</h1>
		</div>
	);
};

export default withAuth(NotebookListPage as React.ComponentType);
